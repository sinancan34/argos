import ky from "ky";
import { parseApiError } from "./errors";

export const api = ky.create({
  prefixUrl: `${import.meta.env.VITE_API_BASE_URL}/api/v1`,
  hooks: {
    beforeError: [
      async (error) => {
        const apiError = error.response
          ? await parseApiError(error.response)
          : null;
        if (apiError) {
          (error as unknown as Record<string, unknown>).apiError = apiError;
          error.message = apiError.error.message;
        }
        return error;
      },
    ],
  },
});
