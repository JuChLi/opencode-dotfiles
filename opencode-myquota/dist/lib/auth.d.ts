import type { AuthData, MiniMaxAuthNode } from "./types";
export declare function loadAuthData(): Promise<{
    authPath: string;
    auth?: AuthData;
    error?: string;
}>;
export declare function extractMiniMaxNode(auth: AuthData | undefined): {
    node?: MiniMaxAuthNode;
    sourceKey?: string;
};
export declare function extractApiKey(node: MiniMaxAuthNode | undefined): string | undefined;
export declare function extractGroupId(node: MiniMaxAuthNode | undefined): string | undefined;
//# sourceMappingURL=auth.d.ts.map