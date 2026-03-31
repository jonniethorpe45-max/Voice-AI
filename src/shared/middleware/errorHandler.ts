import type { FastifyError, FastifyReply, FastifyRequest } from "fastify";
import { ZodError } from "zod";

export class AppError extends Error {
  statusCode: number;
  code?: string;

  constructor(message: string, statusCode = 400, code?: string) {
    super(message);
    this.statusCode = statusCode;
    this.code = code;
  }
}

export function errorHandler(
  error: FastifyError | AppError | ZodError,
  _request: FastifyRequest,
  reply: FastifyReply,
): void {
  if (error instanceof ZodError) {
    reply.status(400).send({ error: error.issues.map((x) => x.message).join(", "), code: "VALIDATION_ERROR" });
    return;
  }

  const statusCode = (error as AppError).statusCode ?? 500;
  const message = statusCode === 500 ? "Internal server error" : error.message;
  reply.status(statusCode).send({ error: message, code: (error as AppError).code });
}
