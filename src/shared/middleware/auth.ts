import type { FastifyReply, FastifyRequest } from "fastify";
import jwt from "jsonwebtoken";

import { env } from "../../config/env";
import { prisma } from "../../db/client";

type AccessClaims = {
  sub: string;
  email: string;
  name: string;
  role: "admin" | "reviewer";
  iat: number;
  exp: number;
};

export async function requireAuth(request: FastifyRequest, reply: FastifyReply): Promise<void> {
  const auth = request.headers.authorization;
  if (!auth || !auth.startsWith("Bearer ")) {
    reply.status(401).send({ error: "Unauthorized" });
    return;
  }

  const token = auth.slice("Bearer ".length);
  let claims: AccessClaims;
  try {
    claims = jwt.verify(token, env.JWT_SECRET) as unknown as AccessClaims;
  } catch {
    reply.status(401).send({ error: "Unauthorized" });
    return;
  }

  const user = await prisma.user.findUnique({ where: { id: claims.sub } });
  if (!user) {
    reply.status(401).send({ error: "Unauthorized" });
    return;
  }

  request.user = {
    id: user.id,
    email: user.email,
    name: user.name,
    role: user.role === "ADMIN" ? "admin" : "reviewer",
  };
}
