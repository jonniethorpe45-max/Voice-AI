import { NotificationEventType } from "@prisma/client";

import { prisma } from "../../db/client";
import { dbNotificationTypeToApi } from "../../shared/utils/statusMappings";

export class NotificationsService {
  async list() {
    const unread = await prisma.notificationEvent.findMany({ where: { isRead: false }, orderBy: { createdAt: "desc" } });
    const read = await prisma.notificationEvent.findMany({ where: { isRead: true }, orderBy: { createdAt: "desc" }, take: 50 });
    return [...unread, ...read]
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
      .map((n) => ({
        id: n.id,
        type: dbNotificationTypeToApi(n.type),
        lead_id: n.leadId,
        lead_owner_name: n.leadOwnerName,
        message: n.message,
        created_at: n.createdAt.toISOString(),
        is_read: n.isRead,
      }));
  }

  async markRead(id: string) {
    await prisma.notificationEvent.update({ where: { id }, data: { isRead: true } });
  }

  async readAll() {
    await prisma.notificationEvent.updateMany({ data: { isRead: true } });
  }

  async create(input: { type: NotificationEventType; leadId: string; leadOwnerName?: string | null; message?: string | null }) {
    return prisma.notificationEvent.create({
      data: {
        type: input.type,
        leadId: input.leadId,
        leadOwnerName: input.leadOwnerName ?? null,
        message: input.message ?? null,
      },
    });
  }
}

export const notificationsService = new NotificationsService();
