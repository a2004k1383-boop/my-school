import { z } from 'zod'

import { fa } from '@/shared/i18n/fa'

const email = z.string().trim().min(1, fa.auth.errors.emailRequired).email(fa.auth.errors.emailInvalid)

const password = z
  .string()
  .min(1, fa.auth.errors.passwordRequired)
  .min(8, fa.auth.errors.passwordShort)
  .regex(/[A-Za-z]/, fa.auth.errors.passwordWeak)
  .regex(/[0-9]/, fa.auth.errors.passwordWeak)

export const loginSchema = z.object({
  email,
  password: z.string().min(1, fa.auth.errors.passwordRequired),
})

export const registerSchema = z
  .object({
    full_name: z.string().trim().min(3, fa.auth.errors.nameRequired),
    email,
    password,
    password_confirm: z.string().min(1, fa.auth.errors.passwordRequired),
    role: z.enum(['parent', 'student', 'teacher'], {
      errorMap: () => ({ message: fa.auth.errors.roleRequired }),
    }),
    invite_code: z.string().optional(),
    accepted_terms: z.boolean(),
  })
  .superRefine((values, ctx) => {
    if (values.password !== values.password_confirm) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ['password_confirm'],
        message: fa.auth.errors.passwordMismatch,
      })
    }
    if (values.role === 'teacher' && !(values.invite_code ?? '').trim()) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ['invite_code'],
        message: fa.auth.errors.inviteRequired,
      })
    }
    if (!values.accepted_terms) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ['accepted_terms'],
        message: fa.auth.errors.termsRequired,
      })
    }
  })

export type LoginValues = z.infer<typeof loginSchema>
export type RegisterValues = z.infer<typeof registerSchema>

/** Convert zod issues into a `field -> message` map used by the form components. */
export function issuesToFields(error: z.ZodError): Record<string, string> {
  const fields: Record<string, string> = {}
  for (const issue of error.issues) {
    const key = issue.path.join('.') || 'form'
    if (!(key in fields)) {
      fields[key] = issue.message
    }
  }
  return fields
}
