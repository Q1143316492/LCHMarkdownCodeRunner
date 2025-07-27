import * as vscode from 'vscode';
import { spawn } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

interface GMDirective {
    line: number;
    args: string[];
    params: { [key: string]: string };
    codeBlock: string;
    startLine: number;
    endLine: number;
    gmIdentifier: string; // 添加GM标识符字段
}

interface PythonCodeBlock {
    content: string;
    startLine: number;
    endLine: number;
    gmDirective?: GMDirective;
}

class MarkdownCodeLensProvider implements vscode.CodeLensProvider {
    private _onDidChangeCodeLenses: vscode.EventEmitter<void> = new vscode.EventEmitter<void>();
    public readonly onDidChangeCodeLenses: vscode.Event<void> = this._onDidChangeCodeLenses.event;

    provideCodeLenses(document: vscode.TextDocument, token: vscode.CancellationToken): vscode.CodeLens[] | Thenable<vscode.CodeLens[]> {
        if (document.languageId !== 'markdown') {
            return [];
        }

        const codeLenses: vscode.CodeLens[] = [];
        const codeBlocks = this.findPythonCodeBlocksWithGM(document);

        for (const block of codeBlocks) {
            if (block.gmDirective) {
                const range = new vscode.Range(block.gmDirective.line, 0, block.gmDirective.line, 0);
                const command: vscode.Command = {
                    title: '▶️ Run Code',
                    command: 'lch-markdown-code-runner.runPythonCode',
                    arguments: [document, block]
                };
                codeLenses.push(new vscode.CodeLens(range, command));
            }
        }

        return codeLenses;
    }

    private findPythonCodeBlocksWithGM(document: vscode.TextDocument): PythonCodeBlock[] {
        const text = document.getText();
        const lines = text.split('\n');
        const blocks: PythonCodeBlock[] = [];
        
        let inPythonBlock = false;
        let currentBlock: PythonCodeBlock | null = null;
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            
            if (line.trim().startsWith('```python')) {
                inPythonBlock = true;
                currentBlock = {
                    content: '',
                    startLine: i + 1,
                    endLine: -1
                };
            } else if (line.trim() === '```' && inPythonBlock && currentBlock) {
                currentBlock.endLine = i - 1;
                inPythonBlock = false;
                
                // Check for GM directive in the block
                const gmDirective = this.findGMDirective(currentBlock.content, currentBlock.startLine);
                if (gmDirective) {
                    currentBlock.gmDirective = gmDirective;
                    blocks.push(currentBlock);
                }
                currentBlock = null;
            } else if (inPythonBlock && currentBlock) {
                currentBlock.content += line + '\n';
            }
        }
        
        return blocks;
    }

    private findGMDirective(content: string, startLine: number): GMDirective | null {
        const config = vscode.workspace.getConfiguration('lchMarkdownCodeRunner');
        const gmConfigs = config.get<{ [key: string]: any }>('gmConfigs', {});
        
        const lines = content.split('\n');
        
        for (let i = 0; i < lines.length; i++) {
            const line = lines[i].trim();
            
            // 检查所有配置的GM标识符
            for (const gmIdentifier of Object.keys(gmConfigs)) {
                // 修改正则表达式，确保GM标识符是完整匹配，后面必须是 [ 或行结束
                const gmPattern = new RegExp(`^#\\s*${gmIdentifier}(?=\\[|$)(?:\\[([^\\]]+)\\])?`);
                const match = line.match(gmPattern);
                
                if (match) {
                    const directive: GMDirective = {
                        line: startLine + i,
                        args: [],
                        params: {},
                        codeBlock: content,
                        startLine: startLine,
                        endLine: startLine + lines.length - 1,
                        gmIdentifier: gmIdentifier
                    };
                    
                    if (match[1]) {
                        // Parse parameters
                        const paramStr = match[1];
                        const parts = paramStr.split(',').map(p => p.trim());
                        
                        for (const part of parts) {
                            if (part.includes('=')) {
                                const [key, value] = part.split('=', 2);
                                directive.params[key.trim()] = value.trim();
                            } else {
                                directive.args.push(part);
                            }
                        }
                    }
                    
                    return directive;
                }
            }
        }
        
        return null;
    }

    refresh(): void {
        this._onDidChangeCodeLenses.fire();
    }
}

export function activate(context: vscode.ExtensionContext) {
    console.log('LCH Markdown Code Runner is now active!');

    const outputChannel = vscode.window.createOutputChannel('LCH Markdown Code Runner');
    const codeLensProvider = new MarkdownCodeLensProvider();

    // Register CodeLens provider
    context.subscriptions.push(
        vscode.languages.registerCodeLensProvider('markdown', codeLensProvider)
    );

    // Register the run command
    const runCommand = vscode.commands.registerCommand(
        'lch-markdown-code-runner.runPythonCode',
        async (document: vscode.TextDocument, block: PythonCodeBlock) => {
            await runPythonCode(document, block, outputChannel);
        }
    );

    context.subscriptions.push(runCommand);

    // Refresh CodeLens when configuration changes
    const configChangeListener = vscode.workspace.onDidChangeConfiguration(e => {
        if (e.affectsConfiguration('lchMarkdownCodeRunner')) {
            codeLensProvider.refresh();
        }
    });

    context.subscriptions.push(configChangeListener);

    // Refresh CodeLens when document changes
    const documentChangeListener = vscode.workspace.onDidChangeTextDocument(e => {
        if (e.document.languageId === 'markdown') {
            codeLensProvider.refresh();
        }
    });

    context.subscriptions.push(documentChangeListener);
}

async function runPythonCode(document: vscode.TextDocument, block: PythonCodeBlock, outputChannel: vscode.OutputChannel) {
    if (!block.gmDirective) {
        return;
    }

    const config = vscode.workspace.getConfiguration('lchMarkdownCodeRunner');
    const gmConfigs = config.get<{ [key: string]: any }>('gmConfigs', {});

    // 添加调试信息
    outputChannel.clear();
    outputChannel.show();
    outputChannel.appendLine('='.repeat(50));
    outputChannel.appendLine(`Running Python code from ${document.fileName}`);
    // outputChannel.appendLine(`Debug: Read gmConfigs from configuration:`);
    // outputChannel.appendLine(JSON.stringify(gmConfigs, null, 2));
    
    // 获取当前GM标识符对应的配置
    const gmIdentifier = block.gmDirective.gmIdentifier;
    // outputChannel.appendLine(`Debug: Looking for GM identifier: ${gmIdentifier}`);
    
    const gmConfig = gmConfigs[gmIdentifier];
    
    if (!gmConfig) {
        outputChannel.appendLine(`❌ 未找到 ${gmIdentifier} 的配置`);
        outputChannel.appendLine(`Available GM identifiers: ${Object.keys(gmConfigs).join(', ')}`);
        return;
    }
    
    // outputChannel.appendLine(`Debug: Found config for ${gmIdentifier}:`);
    outputChannel.appendLine(JSON.stringify(gmConfig, null, 2));

    const scriptPath = gmConfig.scriptPath;
    const commandTemplate = gmConfig.commandTemplate || 'python {scriptPath} {args}';
    const timeout = gmConfig.timeout || 30000;
    const passCodeAsStdin = gmConfig.passCodeAsStdin !== undefined ? gmConfig.passCodeAsStdin : true;
    const passCodeAsFile = gmConfig.passCodeAsFile !== undefined ? gmConfig.passCodeAsFile : false;

    outputChannel.appendLine(`GM Identifier: ${gmIdentifier}`);
    outputChannel.appendLine(`Script Path: ${scriptPath}`);
    outputChannel.appendLine(`Command Template: ${commandTemplate}`);
    outputChannel.appendLine(`Pass Code As Stdin: ${passCodeAsStdin}`);
    outputChannel.appendLine(`Pass Code As File: ${passCodeAsFile}`);
    outputChannel.appendLine(`Timeout: ${timeout}`);
    outputChannel.appendLine(`GM Directive args: ${JSON.stringify(block.gmDirective.args)}`);
    outputChannel.appendLine(`GM Directive params: ${JSON.stringify(block.gmDirective.params)}`);
    outputChannel.appendLine('='.repeat(50));

    try {
        // Remove GM directive line from code
        const lines = block.content.split('\n');
        const filteredLines = lines.filter((line: string) => {
            // 使用当前的GM标识符过滤
            const gmPattern = new RegExp(`^\\s*#\\s*${gmIdentifier}`);
            return !gmPattern.test(line.trim());
        });
        const codeToExecute = filteredLines.join('\n').trim();

        if (!codeToExecute) {
            outputChannel.appendLine('No code to execute after removing GM directive.');
            return;
        }

        // Build command arguments
        let args = '';
        
        // Add positional arguments
        if (block.gmDirective.args.length > 0) {
            args += ' ' + block.gmDirective.args.join(' ');
        }

        // Add named parameters
        for (const [key, value] of Object.entries(block.gmDirective.params)) {
            args += ` --${key}=${value}`;
        }

        // Check execution mode priority:
        // 1. GM directive parameter: direct=true
        // 2. GM directive argument: 'direct'
        const shouldExecuteDirect = 
            block.gmDirective.params['direct'] === 'true' ||
            block.gmDirective.args.includes('direct');

        outputChannel.appendLine('Code to execute:');
        outputChannel.appendLine('─'.repeat(30));
        outputChannel.appendLine(codeToExecute);
        outputChannel.appendLine('─'.repeat(30));

        if (shouldExecuteDirect) {
            // Execute Python code directly using temporary file
            outputChannel.appendLine(`Executing directly: python <temp_file>`);
            await executeDirectPython(codeToExecute, outputChannel, timeout);
        } else {
            // Execute via script
            let command = commandTemplate;
            let tempFilePath = '';

            // Handle code passing methods
            if (passCodeAsFile) {
                // Save code to temporary file
                tempFilePath = path.join(os.tmpdir(), `lch_markdown_code_${Date.now()}.py`);
                fs.writeFileSync(tempFilePath, codeToExecute, 'utf8');
                command = command.replace('{code}', tempFilePath);
                args += ` --code-file="${tempFilePath}"`;
                outputChannel.appendLine(`Code saved to temporary file: ${tempFilePath}`);
            } else {
                command = command.replace('{code}', '');
            }

            // Replace other placeholders
            command = command
                .replace('{scriptPath}', scriptPath)
                .replace('{args}', args.trim());

            outputChannel.appendLine(`Executing: ${command}`);
            
            if (passCodeAsStdin) {
                await executeCommandWithStdin(command, codeToExecute, outputChannel, timeout);
            } else {
                await executeCommand(command, '', outputChannel, timeout);
            }

            // Clean up temporary file
            if (tempFilePath && fs.existsSync(tempFilePath)) {
                fs.unlinkSync(tempFilePath);
                outputChannel.appendLine(`Temporary file cleaned up: ${tempFilePath}`);
            }
        }

    } catch (error) {
        outputChannel.appendLine(`Error: ${error}`);
    }
}

function executeDirectPython(code: string, outputChannel: vscode.OutputChannel, timeout: number): Promise<void> {
    return new Promise((resolve, reject) => {
        // For direct execution, save code to a temporary file to handle multi-line code properly
        const tempFilePath = path.join(os.tmpdir(), `lch_direct_exec_${Date.now()}.py`);
        
        try {
            fs.writeFileSync(tempFilePath, code, 'utf8');
            
            outputChannel.appendLine(`Created temporary file: ${tempFilePath}`);
            outputChannel.appendLine(`Executing command: python ${tempFilePath}`);
            
            const child = spawn('python', [tempFilePath], {
                shell: true,
                cwd: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath,
                env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
            });

            let outputData = '';
            let errorData = '';

            child.stdout?.on('data', (data) => {
                const output = data.toString('utf8');
                outputData += output;
                outputChannel.append(output);
            });

            child.stderr?.on('data', (data) => {
                const error = data.toString('utf8');
                errorData += error;
                outputChannel.append(`[ERROR] ${error}`);
            });

            child.on('close', (code) => {
                // Clean up temporary file
                try {
                    fs.unlinkSync(tempFilePath);
                } catch (e) {
                    // Ignore cleanup errors
                }
                
                outputChannel.appendLine('─'.repeat(50));
                outputChannel.appendLine(`Process exited with code: ${code}`);
                
                if (code === 0) {
                    outputChannel.appendLine('✅ Execution completed successfully');
                } else {
                    outputChannel.appendLine('❌ Execution failed');
                }
                
                resolve();
            });

            child.on('error', (error) => {
                // Clean up temporary file
                try {
                    fs.unlinkSync(tempFilePath);
                } catch (e) {
                    // Ignore cleanup errors
                }
                
                outputChannel.appendLine(`[SPAWN ERROR] ${error.message}`);
                reject(error);
            });

            // Set timeout
            const timer = setTimeout(() => {
                outputChannel.appendLine('⏰ Execution timed out, killing process...');
                child.kill('SIGKILL');
                resolve();
            }, timeout);

            child.on('close', () => {
                clearTimeout(timer);
            });
            
        } catch (error) {
            outputChannel.appendLine(`[FILE ERROR] Failed to create temporary file: ${(error as Error).message}`);
            reject(error);
        }
    });
}

function executeCommandWithStdin(command: string, code: string, outputChannel: vscode.OutputChannel, timeout: number): Promise<void> {
    return new Promise((resolve, reject) => {
        const parts = command.split(' ');
        const cmd = parts[0];
        const args = parts.slice(1);

        const child = spawn(cmd, args, {
            shell: true,
            cwd: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath,
            env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
        });

        // Send code to stdin
        if (code && child.stdin) {
            child.stdin.write(code);
            child.stdin.end();
        }

        let outputData = '';
        let errorData = '';

        child.stdout?.on('data', (data) => {
            const output = data.toString('utf8');
            outputData += output;
            outputChannel.append(output);
        });

        child.stderr?.on('data', (data) => {
            const error = data.toString('utf8');
            errorData += error;
            outputChannel.append(`[ERROR] ${error}`);
        });

        child.on('close', (code) => {
            outputChannel.appendLine('─'.repeat(50));
            outputChannel.appendLine(`Process exited with code: ${code}`);
            
            if (code === 0) {
                outputChannel.appendLine('✅ Execution completed successfully');
            } else {
                outputChannel.appendLine('❌ Execution failed');
            }
            
            resolve();
        });

        child.on('error', (error) => {
            outputChannel.appendLine(`[SPAWN ERROR] ${error.message}`);
            reject(error);
        });

        // Set timeout
        const timer = setTimeout(() => {
            outputChannel.appendLine('⏰ Execution timed out, killing process...');
            child.kill('SIGKILL');
            resolve();
        }, timeout);

        child.on('close', () => {
            clearTimeout(timer);
        });
    });
}

function executeCommand(command: string, code: string, outputChannel: vscode.OutputChannel, timeout: number): Promise<void> {
    return new Promise((resolve, reject) => {
        const parts = command.split(' ');
        const cmd = parts[0];
        const args = parts.slice(1);

        const child = spawn(cmd, args, {
            shell: true,
            cwd: vscode.workspace.workspaceFolders?.[0]?.uri.fsPath,
            env: { ...process.env, PYTHONIOENCODING: 'utf-8' }
        });

        // Send code to stdin if needed
        if (code && child.stdin) {
            child.stdin.write(code);
            child.stdin.end();
        }

        let outputData = '';
        let errorData = '';

        child.stdout?.on('data', (data) => {
            const output = data.toString('utf8');
            outputData += output;
            outputChannel.append(output);
        });

        child.stderr?.on('data', (data) => {
            const error = data.toString('utf8');
            errorData += error;
            outputChannel.append(`[ERROR] ${error}`);
        });

        child.on('close', (code) => {
            outputChannel.appendLine('─'.repeat(50));
            outputChannel.appendLine(`Process exited with code: ${code}`);
            
            if (code === 0) {
                outputChannel.appendLine('✅ Execution completed successfully');
            } else {
                outputChannel.appendLine('❌ Execution failed');
            }
            
            resolve();
        });

        child.on('error', (error) => {
            outputChannel.appendLine(`[SPAWN ERROR] ${error.message}`);
            reject(error);
        });

        // Set timeout
        const timer = setTimeout(() => {
            outputChannel.appendLine('⏰ Execution timed out, killing process...');
            child.kill('SIGKILL');
            resolve();
        }, timeout);

        child.on('close', () => {
            clearTimeout(timer);
        });
    });
}

export function deactivate() {}
