interface ApiErrorDetail {
  loc: string[];
  message: string;
  type: string;
}

interface ApiErrorBody {
  code: string;
  message: string;
  details: ApiErrorDetail[];
}

interface ApiError {
  error: ApiErrorBody;
}

function isApiError(value: unknown): value is ApiError {
  return (
    typeof value === "object" &&
    value !== null &&
    "error" in value &&
    typeof (value as ApiError).error?.code === "string"
  );
}

export async function parseApiError(
  response: Response,
): Promise<ApiError | null> {
  try {
    const body: unknown = await response.clone().json();
    return isApiError(body) ? body : null;
  } catch {
    return null;
  }
}
