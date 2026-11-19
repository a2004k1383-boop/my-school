import { ApiError } from '@/shared/api/http'
import { fa } from '@/shared/i18n/fa'

const CODE_MESSAGES: Record<string, string> = {
  invalid_credentials: fa.errors.invalidCredentials,
  email_already_registered: fa.errors.emailTaken,
  invitation_required: fa.errors.invitationRequired,
  account_disabled: fa.errors.accountDisabled,
  rate_limited: fa.errors.rateLimited,
  csrf_failed: fa.errors.csrfFailed,
  network_error: fa.errors.network,
}

/** Translate any thrown error into a safe Persian message. */
export function toMessage(error: unknown): string {
  if (error instanceof ApiError) {
    return CODE_MESSAGES[error.code] ?? fa.errors.generic
  }
  return fa.errors.generic
}
