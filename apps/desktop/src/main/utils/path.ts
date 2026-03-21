import { pathToFileURL } from 'node:url';

export const filePathToAppUrl = (filePath: string) => {
  return `app://coze2jianying.com${pathToFileURL(filePath).pathname}`;
};
