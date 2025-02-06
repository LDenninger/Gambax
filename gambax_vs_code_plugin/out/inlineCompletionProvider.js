"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.InlineCompletionManager = void 0;
const vscode = require("vscode");
class InlineCompletionProvider {
    provideInlineCompletionItems(document, position, context, token) {
        // Only process automatic triggers if the idle time has been met
        // Otherwise, produce and return your inline completions
        const completion = new vscode.InlineCompletionItem('Your suggestion here');
        return [completion];
    }
}
/**
 * A template class for managing inline completions.
 */
class InlineCompletionManager {
    constructor(context) {
        this.context = context;
        // You can adjust the idle delay as needed (in milliseconds).
        this.idleDelay = 2000;
        // Optionally, initialize any resources or event listeners here.
    }
    /**
     * Requests an inline completion.
     *
     * @param document The current text document.
     * @param position The current cursor position.
     * @param triggerContext The inline completion trigger context.
     * @returns A promise that resolves when the request is complete.
     */
    async request(document, position, triggerContext) {
        // Example: if the trigger is automatic, wait for the idle delay.
        if (triggerContext.triggerKind === vscode.InlineCompletionTriggerKind.Automatic) {
            await this.waitForIdle();
        }
        // Generate a sample inline completion.
        // In a real implementation, you might call an API or generate a suggestion dynamically.
        const suggestion = 'This is a sample inline completion';
        // Create a dummy range where the completion will be inserted.
        // Here we use a zero-length range at the current cursor position.
        const range = new vscode.Range(position, position);
        // Create the inline completion item.
        this.lastCompletion = new vscode.InlineCompletionItem(suggestion, range);
    }
    /**
     * Returns the last inline completion that was generated.
     *
     * @returns The last inline completion item or null if none exists.
     */
    getCompletion() {
        return this.lastCompletion;
    }
    /**
     * Helper function that returns a promise resolved after the configured idle delay.
     */
    waitForIdle() {
        return new Promise((resolve) => setTimeout(resolve, this.idleDelay));
    }
}
exports.InlineCompletionManager = InlineCompletionManager;
//# sourceMappingURL=inlineCompletionProvider.js.map