/**
 * Shared types (MiniMax only)
 */
export interface QueryResult {
  success: boolean;
  output?: string;
  error?: string;
}

export type MiniMaxAuthNode = {
  type?: string;
  key?: string;
  api_key?: string;
  token?: string;

  groupId?: string;
  GroupId?: string;
  group_id?: string;
  groupID?: string;
  group?: string;
};

export interface AuthData {
  "minimax-coding-plan"?: MiniMaxAuthNode;
  minimax?: MiniMaxAuthNode;
}

/** Request timeout in milliseconds */
export const REQUEST_TIMEOUT_MS = 10000;
