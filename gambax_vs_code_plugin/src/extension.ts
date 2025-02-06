import * as vscode from 'vscode';
import { Range } from 'vscode';
import fetch from 'node-fetch';

// Global configuration variables.
let debounceDelay: number = 1000;
let contextWindowSize: number = 5;

// Global variables for debouncing the API call.
let debounceTimer: NodeJS.Timeout | undefined;
let globalPromise: Promise<string> | undefined;
let lastContext:
  | {
      document: vscode.TextDocument;
      position: vscode.Position;
      completionContext: vscode.InlineCompletionContext;
    }
  | undefined;

export function activate(context: vscode.ExtensionContext) {
  console.log('LLM inline-completion demo started');

  // Read configuration values.
  const config = vscode.workspace.getConfiguration('gambax');
  debounceDelay = config.get<number>('debounceDelay', 1000);
  contextWindowSize = config.get<number>('contextWindowSize', 5);

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
      } else {
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
      } else {
        vscode.window.showErrorMessage('Invalid input. Please enter a valid number.');
      }
    }
  });

  const provider: vscode.InlineCompletionItemProvider = {
    async provideInlineCompletionItems(document, position, completionContext, token) {
      // Get the current line text.
      const currentLine = document.lineAt(position.line).text;

      // 1. Only provide inline completions if the cursor is at the end of the line.
      if (position.character !== currentLine.length) {
        return { items: [] };
      }

      // 2. Do not complete if the line is a comment.
      // Use the document's languageId to decide which comment marker to use.
      const languageId = document.languageId;
      const trimmedLine = currentLine.trimStart();
      if (
        (languageId === 'python' && trimmedLine.startsWith('#')) ||
        (languageId === 'cpp' && trimmedLine.startsWith('//'))
      ) {
        return { items: [] };
      }

      // 3. If an API call for this same line is already pending, simply await it.
      if (
        globalPromise &&
        lastContext &&
        lastContext.document.uri.toString() === document.uri.toString() &&
        lastContext.position.line === position.line &&
        lastContext.position.character === position.character
      ) {
        try {
          const completionText = await globalPromise;
          if (token.isCancellationRequested || !completionText) {
            return { items: [] };
          }
          return createInlineCompletionItem(position, completionText);
        } catch (e) {
          return { items: [] };
        }
      } else {
        // If a pending call exists for a different location, cancel it.
        if (debounceTimer) {
          clearTimeout(debounceTimer);
          debounceTimer = undefined;
        }
        globalPromise = undefined;
      }

      // Update the context so that the latest parameters are used.
      lastContext = { document, position, completionContext };

      // Create a new promise for the API call (debounced).
      globalPromise = new Promise<string>((resolve, reject) => {
        debounceTimer = setTimeout(async () => {
          if (!lastContext) {
            resolve('');
            return;
          }
          const { document, position } = lastContext;

          // Gather context lines before the current position.
          const previousLines: string[] = [];
          for (let i = position.line - 1; i >= 0 && previousLines.length < contextWindowSize; i--) {
            const lineText = document.lineAt(i).text;
            if (lineText.trim().length > 0) {
              previousLines.unshift(lineText);
            }
          }

          // Gather context lines after the current position.
          const upcomingLines: string[] = [];
          for (let i = position.line + 1; i < document.lineCount && upcomingLines.length < contextWindowSize; i++) {
            const lineText = document.lineAt(i).text;
            if (lineText.trim().length > 0) {
              upcomingLines.push(lineText);
            }
          }

          const contextBefore = previousLines.join('\n');
          const currentLine = document.lineAt(position).text;
          const contextAfter = upcomingLines.join('\n');

          // Use the file extension to provide language info if needed.
          const fileName = document.fileName;
          const dotIndex = fileName.lastIndexOf('.');
          const language = dotIndex >= 0 ? fileName.substring(dotIndex + 1).toLowerCase() : 'plaintext';

          console.log('Context for LLM:', { contextBefore, line: currentLine, contextAfter });

          // Call the LLM server.
          const serverUrl = 'http://localhost:5000/request_service/inline_completion';
          let completionText = '';
          try {
            const response = await fetch(serverUrl, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                context_before: contextBefore,
                line: currentLine,
                context_after: contextAfter,
                language: language,
              }),
            });

            if (!response.ok) {
              console.error(`LLM server responded with status ${response.status}`);
              resolve('');
              return;
            }

            const data = await response.json();
            completionText = data.response;
            console.log('LLM completion (from API):', data);
          } catch (error) {
            console.error('Error calling LLM server:', error);
            resolve('');
            return;
          } finally {
            // Clear the global promise and timer so that future requests can start fresh.
            globalPromise = undefined;
            debounceTimer = undefined;
          }
          resolve(completionText);
        }, debounceDelay);
      });

      try {
        const completionText = await globalPromise;
        if (token.isCancellationRequested || !completionText) {
          return { items: [] };
        }
        return createInlineCompletionItem(position, completionText);
      } catch (e) {
        return { items: [] };
      }
    },
  };

  context.subscriptions.push(
    vscode.languages.registerInlineCompletionItemProvider({ pattern: '**' }, provider)
  );
}

/**
 * Helper function to create an inline completion item given the starting position and the text.
 */
function createInlineCompletionItem(
  position: vscode.Position,
  completionText: string
): vscode.InlineCompletionList {
  const lines = completionText.split('\n');
  const lastLineLength = lines[lines.length - 1].length;
  const lineOffset = lines.length - 1;
  const endPosition = position.with({
    line: position.line + lineOffset,
    character: lastLineLength,
  });

  const inlineItem: vscode.InlineCompletionItem = {
    insertText: completionText,
    range: new Range(position, endPosition),
  };

  return { items: [inlineItem] };
}
