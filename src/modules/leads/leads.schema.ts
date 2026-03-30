import { z } from "zod";

export const listLeadsQuerySchema = z.object({
  state: z.enum(["CA", "FL"]).optional(),
  county: z.string().optional(),
  status: z.string().optional(),
  page: z.coerce.number().int().positive().default(1),
  page_size: z.coerce.number().int().positive().max(200).default(50),
});

export const reasonBodySchema = z.object({ reason: z.string().optional() });
export const notesBodySchema = z.object({ notes: z.string().min(1) });
export const clearLegalReviewSchema = z.object({ legal_review_cleared: z.boolean().default(true) });
