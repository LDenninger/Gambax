"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.activate = activate;
const vscode = require("vscode");
const vscode_1 = require("vscode");
const inlineCompletions_1 = require("./inlineCompletions");
// Global configuration variables.
let debounceDelay = 1000;
let contextWindowSize = 5;
// Global variables for debouncing the API call.
let debounceTimer;
let globalPromise;
let lastContext;
function activate(context) {
    console.log('LLM inline-completion demo started');
    // Read configuration values.
    const config = vscode.workspace.getConfiguration('gambax');
    debounceDelay = config.get('debounceDelay', 1000);
    contextWindowSize = config.get('contextWindowSize', 5);
    // Command to update the debounce delay.
    vscode.commands.registerCommand('gambax.setDebounceDelay', async () => {
        const input = await vscode.window.showInputBox({
            prompt: 'Enter debounce delay in milliseconds:',
            value: debounceDelay.toString(),
        });
        if (input) {
            const newDelay = parseInt(input, 10);
            if (!isNaN(newDelay) && newDelay >= 0) {
                debounceDelay = newDelay;
                await config.update('debounceDelay', newDelay, vscode.ConfigurationTarget.Global);
                vscode.window.showInformationMessage(`Debounce delay set to ${newDelay}ms`);
            }
            else {
                vscode.window.showErrorMessage('Invalid input. Please enter a valid number.');
            }
        }
    });
    // Command to update the context window size.
    vscode.commands.registerCommand('gambax.setContextWindow', async () => {
        const input = await vscode.window.showInputBox({
            prompt: 'Enter number of lines in context:',
            value: contextWindowSize.toString(),
        });
        if (input) {
            const newSize = parseInt(input, 10);
            if (!isNaN(newSize) && newSize >= 0) {
                contextWindowSize = newSize;
                await config.update('contextWindowSize', newSize, vscode.ConfigurationTarget.Global);
                vscode.window.showInformationMessage(`Context window size set to ${newSize} lines`);
            }
            else {
                vscode.window.showErrorMessage('Invalid input. Please enter a valid number.');
            }
        }
    });
    // Define the idle delay (in milliseconds)
    let idleTimer;
    const inlineCompletions = new inlineCompletions_1.InlineCompletions('http://localhost:5000/request_service/inline_completion', contextWindowSize);
    const provider = {
        async provideInlineCompletionItems(document, position, completionContext, token) {
            // Reset the timer on every text change
            if (idleTimer) {
                clearTimeout(idleTimer);
            }
            return new Promise((resolve) => {
                idleTimer = setTimeout(async () => {
                    try {
                        // Get the current line text
                        const currentLine = document.lineAt(position.line).text;
                        // Only provide inline completions if the cursor is at the end of the line
                        if (position.character !== currentLine.length) {
                            resolve(undefined);
                            return;
                        }
                        // Check if the current line is a comment
                        const isComment = currentLine.trim().startsWith('//') || currentLine.trim().startsWith('/*');
                        if (isComment) {
                            resolve(undefined);
                            return;
                        }
                        // Get completion from InlineCompletions
                        const completionText = await inlineCompletions.getCompletion(document, position);
                        if (completionText) {
                            // Create and return the inline completion item
                            const completionItem = createInlineCompletionItem(position, completionText);
                            resolve(completionItem);
                        }
                        else {
                            resolve(undefined);
                        }
                    }
                    catch (error) {
                        console.error('Error in provideInlineCompletionItems:', error);
                        resolve(undefined);
                    }
                }, debounceDelay);
            });
        },
    };
    context.subscriptions.push(vscode.languages.registerInlineCompletionItemProvider({ pattern: '**' }, provider));
}
/**
 * Helper function to create an inline completion item given the starting position and the text.
 */
function createInlineCompletionItem(position, completionText) {
    const lines = completionText.split('\n')[0];
    const endPosition = position.with({
        line: position.line,
        character: position.character + completionText.length,
    });
    console.log('Created inline completion item:', completionText, position, endPosition);
    const inlineItem = {
        insertText: completionText,
        range: new vscode_1.Range(position, endPosition),
    };
    return { items: [inlineItem] };
}
//# sourceMappingURL=extension.js.map