export type Role = 'parent' | 'student' | 'teacher'

export interface User {
  id: string
  full_name: string
  email: string
  role: Role
  is_active: boolean
  created_at: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  expires_in: number
  user: User
}

export interface LoginPayload {
  email: string
  password: string
  remember_me: boolean
}

export interface RegisterPayload {
  full_name: string
  email: string
  password: string
  password_confirm: string
  role: Role
  invite_code?: string
  accepted_terms: boolean
}

export interface FieldIssue {
  field: string
  message: string
}

export interface ProblemDetail {
  type?: string
  title?: string
  status?: number
  code?: string
  detail?: string
  errors?: FieldIssue[]
}
