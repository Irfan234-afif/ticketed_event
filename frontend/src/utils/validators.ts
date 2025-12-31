export const validateEmail = (email: string) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export const validatePhone = (phone: string) => {
  // Allow only numbers, spaces, plus sign, and dashes
  const phoneRegex = /^[0-9\s\+\-]+$/
  return phoneRegex.test(phone) && phone.length >= 8
}
