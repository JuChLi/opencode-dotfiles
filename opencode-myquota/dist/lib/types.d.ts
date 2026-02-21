export declare const HIGH_USAGE_THRESHOLD = 80;
export declare const REQUEST_TIMEOUT_MS = 10000;
export interface QueryResult {
    success: boolean;
    output?: string;
    error?: string;
}
export interface MiniMaxAuthNode {
    type?: string;
    key?: string;
    api_key?: string;
    token?: string;
    groupId?: string;
    GroupId?: string;
    group_id?: string;
    groupID?: string;
    group?: string;
}
export interface AuthData {
    "github-copilot"?: CopilotAuthNode;
    openai?: OpenAIAuthNode;
    "zhipuai-coding-plan"?: ZhipuAuthNode;
    "zai-coding-plan"?: ZhipuAuthNode;
    "minimax-coding-plan"?: MiniMaxAuthNode;
    minimax?: MiniMaxAuthNode;
}
export interface CopilotAuthNode {
    type?: string;
    access?: string;
    refresh?: string;
    expires?: number;
}
export interface OpenAIAuthNode {
    type?: string;
    access?: string;
    refresh?: string;
    expires?: number;
}
export interface ZhipuAuthNode {
    type?: string;
    key?: string;
}
//# sourceMappingURL=types.d.ts.map