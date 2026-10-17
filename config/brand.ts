const configuredPhone = process.env.NEXT_PUBLIC_BUSINESS_PHONE;
const phone = configuredPhone === undefined ? "+19175310595" : configuredPhone.trim();
const digits = /^\+?[\d ()\-.]+$/.test(phone) ? phone.replace(/\D/g, "") : "";
export const brand = {
  name: "IP NET SECURITY & LOCKSMITH",
  email: "ipnet.security@gmail.com",
  url: "https://ipnetsecurity.com",
  phoneDisplay: digits === "19175310595" ? "917-531-0595" : phone,
  telephone: digits.length >= 7 && digits.length <= 15 ? `tel:${phone.startsWith("+") ? "+" : ""}${digits}` : null,
  whatsapp: digits.length >= 7 && digits.length <= 15 ? `https://wa.me/${digits}` : null,
};
