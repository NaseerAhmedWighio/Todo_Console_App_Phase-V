import { z } from 'zod'

// Google email domains
const GOOGLE_DOMAINS = ['@gmail.com', '@googlemail.com']

// Email validation regex
const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/

// Helper function to check if email is from Google
export const isGoogleEmail = (email: string): boolean => {
  const emailLower = email.toLowerCase().trim()
  return GOOGLE_DOMAINS.some(domain => emailLower.endsWith(domain))
}

// Helper function to validate email format
export const isValidEmail = (email: string): boolean => {
  return emailRegex.test(email)
}

// Base email schema
export const emailSchema = z.string({
  error: 'Email is required'
})
  .email('Invalid email format')
  .refine(
    (email) => isValidEmail(email),
    { message: 'Invalid email format' }
  )

// Google email schema (requires gmail.com or googlemail.com)
export const googleEmailSchema = emailSchema.refine(
  (email) => isGoogleEmail(email),
  { message: 'Email must be a Google email (gmail.com or googlemail.com)' }
)

// Password schema
export const passwordSchema = z.string({
  error: 'Password is required'
})
  .min(6, 'Password must be at least 6 characters')
  .max(128, 'Password must not exceed 128 characters')
  .regex(
    /^(?=.*[a-zA-Z])(?=.*[0-9!@#$%^&*])/,
    { message: 'Password must contain at least one letter and one number or special character' }
  )

// Name schema
export const nameSchema = z.string({
  error: 'Name is required'
})
  .max(255, 'Name must not exceed 255 characters')
  .regex(
    /^[a-zA-Z\s'-]+$/,
    { message: 'Name can only contain letters, spaces, hyphens, and apostrophes' }
  )

// Registration schema (default - any valid email)
export const registerSchema = z.object({
  name: nameSchema,
  email: emailSchema,
  password: passwordSchema,
  google_email_only: z.boolean().optional().default(false)
})

// Registration schema with Google email requirement
export const registerGoogleSchema = z.object({
  name: nameSchema,
  email: googleEmailSchema,
  password: passwordSchema,
  google_email_only: z.boolean().optional().default(true)
})

// Login schema
export const loginSchema = z.object({
  email: emailSchema,
  password: passwordSchema
})

// Verification token schema
export const verificationTokenSchema = z.string({
  error: 'Verification token is required'
})

// Resend verification schema
export const resendVerificationSchema = z.object({
  email: emailSchema
})

// Type exports
export type RegisterInput = z.infer<typeof registerSchema>
export type RegisterGoogleInput = z.infer<typeof registerGoogleSchema>
export type LoginInput = z.infer<typeof loginSchema>
export type VerificationTokenInput = z.infer<typeof verificationTokenSchema>
export type ResendVerificationInput = z.infer<typeof resendVerificationSchema>

// Validation helper functions
export const validateRegistration = (data: unknown, requireGoogleEmail: boolean = false) => {
  const schema = requireGoogleEmail ? registerGoogleSchema : registerSchema
  return schema.safeParse(data)
}

export const validateLogin = (data: unknown) => {
  return loginSchema.safeParse(data)
}

export const validateEmail = (email: string) => {
  return emailSchema.safeParse(email)
}

export const validatePassword = (password: string) => {
  return passwordSchema.safeParse(password)
}

export const validateName = (name: string) => {
  return nameSchema.safeParse(name)
}
