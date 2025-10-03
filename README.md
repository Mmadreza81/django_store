# 🛒 Django Store Project

یک پروژه فروشگاهی پیشرفته ساخته شده با Django که شامل امکانات احراز هویت، مدیریت محصولات، سفارش‌ها و اتصال به سرویس ابری برای ذخیره‌سازی عکس‌ها است.  

---

## ✨ امکانات پروژه

- احراز هویت:
  - ثبت‌نام با تأیید ایمیل (ارسال کد فعال‌سازی به ایمیل).
  - ورود کاربران (Login).

- مدیریت پروفایل و محصولات:
  - آپلود عکس پروفایل و محصولات روی سرویس ابری Arvan Cloud.
  - قابلیت دانلود و حذف عکس‌ها (فقط توسط ادمین).

- محصولات و تعامل کاربران:
  - قابلیت امتیازدهی به محصولات.
  - سیستم کامنت‌گذاری روی محصولات.
  - نمایش محصولات در صفحه اصلی (۵ محصول در هر صفحه – Pagination).

- سفارش‌ها:
  - ثبت سفارش توسط کاربر.
  - نمایش شماره تماس و آدرس کاربر برای سفارش.

- پنل ادمین:
  - مشاهده و مدیریت سفارشات.
  - مدیریت محصولات و تصاویر.

- Celery + Redis:
  - اجرای وظایف پس‌زمینه (Background tasks).
  - دانلود و حذف عکس‌ها با Celery.
  - حذف رمز عبورهای موقت هر ۲ دقیقه با Celery Beat.
  - Redis به‌عنوان بروکر وظایف (Task Broker).

---

## 📦 نصب و راه‌اندازی

###  کلون کردن پروژه
`bash
git clone https://github.com/Mmadreza81/django_store.git
cd django_store

### ساخت محیط مجازی و فعال سازی
python -m venv venv
source venv/bin/activate   # Linux / Mac   
venv\Scripts\activate      # Windows

### نصب وابستگی ها
pip install -r requirements.txt

### اعمال مایگرشن ها
python manage.py makemigrations
python manage.py migrate

### اجرای سلری ورکر
celery -A project-name worker -l info

### اجرای سلری بیت
celery -A project-name beat -l info

### اجرای سرور
python manage.py runserver