export declare function formatDuration(seconds: number): string;
export declare function createProgressBar(remainPercent: number, width?: number): string;
export declare function calcRemainPercent(usedPercent: number): number;
export declare function formatTokens(tokens: number): string;
export declare function fetchWithTimeout(url: string, options: RequestInit, timeoutMs?: number): Promise<Response>;
export declare function safeMax(arr: number[]): number;
export declare function maskString(str: string, showChars?: number): string;
export declare function normalizeRemainsSeconds(remainsTime: number): number;
//# sourceMappingURL=utils.d.ts.map