import bcrypt from "bcryptjs";
import crypto from "crypto";
import jwt from "jsonwebtoken";
import ms from "ms";

import { env } from "../../config/env";
import { prisma } from "../../db/client";
import { AppError } from "../../shared/middleware/errorHandler";
import { toApiRole } from "../../shared/utils/statusMappings";

function makeAccessToken(user: { id: string; email: string; name: string; role: "ADMIN" | "REVIEWER" }) {
  const expiresIn = env.JWT_EXPIRES_IN as jwt.SignOptions["expiresIn"];
  const access_token = jwt.sign(
    { sub: user.id, email: user.email, name: user.name, role: toApiRole(user.role) },
    env.JWT_SECRET,
    { expiresIn },
  );
  const ttlMs = ms(env.JWT_EXPIRES_IN as ms.StringValue);
  const expires_at = new Date(Date.now() + ttlMs).toISOString();
  return { access_token, expires_at };
}

export class AuthService {
  async login(email: string, password: string) {
    const user = await prisma.user.findUnique({ where: { email: email.toLowerCase() } });
    if (!user) throw new AppError("Invalid credentials", 401);
    const ok = await bcrypt.compare(password, user.passwordHash);
    if (!ok) throw new AppError("Invalid credentials", 401);

    const refresh_token = crypto.randomUUID();
    const expiresAt = new Date(Date.now() + env.REFRESH_TOKEN_EXPIRES_DAYS * 24 * 60 * 60 * 1000);
    await prisma.refreshToken.create({ data: { token: refresh_token, userId: user.id, expiresAt } });

    const token = makeAccessToken(user);
    return {
      id: user.id,
      email: user.email,
      name: user.name,
      role: toApiRole(user.role),
      access_token: token.access_token,
      refresh_token,
      expires_at: token.expires_at,
    };
  }

  async logout(refreshToken?: string, userId?: string): Promise<void> {
    if (refreshToken) {
      await prisma.refreshToken.deleteMany({ where: { token: refreshToken } });
      return;
    }
    if (userId) {
      await prisma.refreshToken.deleteMany({ where: { userId } });
    }
  }

  async refresh(refreshToken: string) {
    const row = await prisma.refreshToken.findUnique({ where: { token: refreshToken }, include: { user: true } });
    if (!row || row.expiresAt.getTime() < Date.now()) {
      throw new AppError("Invalid or expired refresh token", 401);
    }
    return makeAccessToken(row.user);
  }
}

export const authService = new AuthService();
