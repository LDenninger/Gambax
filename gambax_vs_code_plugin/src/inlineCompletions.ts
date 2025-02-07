import * as vscode from 'vscode';
import fetch from 'node-fetch';

export class InlineCompletions {
    private serverUrl: string;
    private contextWindowSize: number;
    private lastRequestLine: number = -1;
    private lastRequestColumn: number = -1;
    private requestPending: boolean = false;

    constructor(serverUrl: string, contextWindowSize: number) {
        this.serverUrl = serverUrl;
        this.contextWindowSize = contextWindowSize;
    }

    public shouldRequest(document: vscode.TextDocument, position: vscode.Position): boolean {
        if (this.requestPending) {
            return false;
        }
        if (this.lastRequestLine == position.line && this.lastRequestColumn == position.character) {
            return false;
        }
        const currentLine = document.lineAt(position.line).text.trim();
        if (currentLine.startsWith('#') || currentLine.startsWith('//')) {
            return false;
        }
        return true;
    }

    async getCompletion(document: vscode.TextDocument, position: vscode.Position): Promise<string> {
        if (!this.shouldRequest(document, position)) {
            if (this.lastRequestLine != position.line) {
                this.lastRequestLine = -1;
            }
            console.warn("Request denied.");
            return '';
        }

        this.lastRequestLine = position.line;
        this.lastRequestColumn = position.character;

        const previousLines = this.getPreviousLines(document, position);
        const upcomingLines = this.getUpcomingLines(document, position);

        const contextBefore = previousLines.join('\n');
        const currentLine = document.lineAt(position).text;
        const contextAfter = upcomingLines.join('\n');

        const language = this.getLanguage(document.fileName);

        console.log('Context for LLM:', { contextBefore, line: currentLine, contextAfter });

        try {
            const response = await fetch(this.serverUrl, {
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
                return '';
            }

            const data = await response.json();
            console.log('LLM completion (from API):', data);
            this.lastRequestColumn = position.character + data.response.length;
            return data.response;
        } catch (error) {
            console.error('Error calling LLM server:', error);
            return '';
        }
    }

    private getPreviousLines(document: vscode.TextDocument, position: vscode.Position): string[] {
        const previousLines: string[] = [];
        for (let i = position.line - 1; i >= 0 && previousLines.length < this.contextWindowSize; i--) {
            const lineText = document.lineAt(i).text;
            if (lineText.trim().length > 0) {
                previousLines.unshift(lineText);
            }
        }
        return previousLines;
    }

    private getUpcomingLines(document: vscode.TextDocument, position: vscode.Position): string[] {
        const upcomingLines: string[] = [];
        for (let i = position.line + 1; i < document.lineCount && upcomingLines.length < this.contextWindowSize; i++) {
            const lineText = document.lineAt(i).text;
            if (lineText.trim().length > 0) {
                upcomingLines.push(lineText);
            }
        }
        return upcomingLines;
    }

    private getLanguage(fileName: string): string {
        const dotIndex = fileName.lastIndexOf('.');
        return dotIndex >= 0 ? fileName.substring(dotIndex + 1).toLowerCase() : 'plaintext';
    }
}