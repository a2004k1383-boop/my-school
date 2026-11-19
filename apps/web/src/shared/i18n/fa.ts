/** Persian copy for the whole application. Components must never hard-code strings. */
export const fa = {
  app: {
    name: 'مدرسه من',
    tagline: 'تکالیف، اطلاعیه‌ها و نمرات، یک‌جا برای خانواده و مدرسه',
  },
  common: {
    loading: 'در حال ارسال…',
    retry: 'تلاش دوباره',
    close: 'بستن',
  },
  roles: {
    parent: 'والد',
    student: 'دانش‌آموز',
    teacher: 'معلم',
  },
  auth: {
    login: {
      title: 'ورود به مدرسه من',
      subtitle: 'برای دیدن تکالیف، نمرات و اطلاعیه‌ها وارد شوید',
      submit: 'ورود',
      noAccount: 'حساب ندارید؟',
      createAccount: 'ثبت‌نام کنید',
    },
    register: {
      title: 'ساخت حساب کاربری',
      subtitle: 'در چند ثانیه حساب خود را بسازید',
      submit: 'ثبت‌نام',
      hasAccount: 'حساب دارید؟',
      signIn: 'وارد شوید',
    },
    fields: {
      fullName: 'نام و نام خانوادگی',
      email: 'ایمیل',
      password: 'رمز عبور',
      passwordConfirm: 'تکرار رمز عبور',
      role: 'نقش خود را انتخاب کنید',
      inviteCode: 'کد دعوت معلم',
      inviteHint: 'کد دعوت را از دفتر مدرسه دریافت کنید.',
      rememberMe: 'مرا به خاطر بسپار',
      acceptTerms: 'قوانین مدرسه را می‌پذیرم',
    },
    actions: {
      showPassword: 'نمایش رمز عبور',
      hidePassword: 'پنهان کردن رمز عبور',
    },
    success: {
      registered: 'حساب شما ساخته شد. اکنون وارد شوید.',
    },
    errors: {
      emailRequired: 'ایمیل را وارد کنید.',
      emailInvalid: 'ایمیل معتبر نیست.',
      passwordRequired: 'رمز عبور را وارد کنید.',
      passwordShort: 'رمز عبور باید حداقل ۸ کاراکتر باشد.',
      passwordWeak: 'رمز عبور باید شامل حرف و رقم باشد.',
      passwordMismatch: 'تکرار رمز عبور مطابقت ندارد.',
      nameRequired: 'نام و نام خانوادگی را وارد کنید.',
      roleRequired: 'نقش خود را انتخاب کنید.',
      inviteRequired: 'کد دعوت معلم را وارد کنید.',
      termsRequired: 'برای ادامه باید قوانین را بپذیرید.',
    },
  },
  dashboard: {
    welcome: 'خوش آمدید',
    roleLabel: 'نقش شما',
    logout: 'خروج',
    comingSoon: 'به‌زودی',
    modules: {
      timetable: 'برنامه هفتگی',
      assignments: 'تکالیف',
      announcements: 'اطلاعیه‌ها',
      grades: 'نمرات و معدل',
    },
    modulesHint: 'این بخش‌ها در فازهای بعدی فعال می‌شوند.',
  },
  errors: {
    invalidCredentials: 'ایمیل یا رمز عبور نادرست است.',
    emailTaken: 'این ایمیل قبلاً ثبت شده است.',
    invitationRequired: 'کد دعوت معلم معتبر نیست.',
    accountDisabled: 'این حساب غیرفعال شده است.',
    rateLimited: 'تلاش‌های زیاد؛ چند دقیقه بعد دوباره امتحان کنید.',
    csrfFailed: 'درخواست نامعتبر است. صفحه را دوباره بارگذاری کنید.',
    network: 'ارتباط با سرور برقرار نشد. اتصال اینترنت را بررسی کنید.',
    generic: 'خطای غیرمنتظره‌ای رخ داد. لطفاً دوباره تلاش کنید.',
  },
} as const

export type MessageKey = string
