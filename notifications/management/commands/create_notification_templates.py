# notifications/management/commands/create_notification_templates.py
from django.core.management.base import BaseCommand
from ...model import NotificationTemplate, NotificationChannel


class Command(BaseCommand):
    help = "Create default notification templates in English and Hindi"

    def add_arguments(self, parser):
        parser.add_argument("--app", type=str, help="Create templates for specific app")
        parser.add_argument(
            "--locale", type=str, help="Create templates for specific locale (en/hi)"
        )

    def handle(self, *args, **options):
        templates = [
            # English Templates
            {
                "name": "mpp_collection_created_en",
                "locale": "en",
                "title_template": "New Milk Collection Recorded: {{ site_name }}",
                "body_template": (
                    "Dear {{ recipient.first_name }},\n\n"
                    "A new milk collection entry has been successfully recorded for Member Code {{ collection.member_code }} "
                    "on {{ collection.collection_date|date:'d M Y, H:i' }} during {{ collection.shift_code }} shift.\n"
                    "Quantity: {{ collection.qty }} L | Fat: {{ collection.fat }} | SNF: {{ collection.snf }}\n\n"
                    "Thank you for maintaining quality and consistency.\n"
                    "- {{ site_name }} Dairy Management System"
                ),
                "email_subject_template": "Milk Collection Confirmation – {{ collection.collection_date|date:'d M Y' }}",
                "email_body_template": (
                    "Hello {{ recipient.first_name }},\n\n"
                    "Your milk collection details have been successfully recorded in {{ site_name }}.\n\n"
                    "**Collection Details:**\n"
                    "- Member Code: {{ collection.member_code }}\n"
                    "- Date: {{ collection.collection_date|date:'d M Y, H:i' }}\n"
                    "- Shift: {{ collection.shift_code }}\n"
                    "- Quantity: {{ collection.qty }} L\n"
                    "- Fat: {{ collection.fat }} | SNF: {{ collection.snf }}\n\n"
                    "For any discrepancies, please contact your collection center.\n\n"
                    "Warm regards,\n"
                    "{{ site_name }} Team"
                ),
                "route_template": "/",
                "category": "mpp_collection",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.PUSH,
                    NotificationChannel.EMAIL,
                ],
            },
            # Hindi Template
            {
                "name": "mpp_collection_created_hi",
                "locale": "hi",
                "title_template": "नया दूध संग्रह दर्ज किया गया: {{ site_name }}",
                "body_template": (
                    "प्रिय {{ recipient.first_name }},\n\n"
                    "सदस्य कोड {{ collection.member_code }} के लिए {{ collection.collection_date|date:'d M Y, H:i' }} को "
                    "{{ collection.shift_code }} शिफ्ट में एक नया दूध संग्रह प्रविष्टि सफलतापूर्वक दर्ज की गई है।\n"
                    "मात्रा: {{ collection.qty }} लीटर | वसा: {{ collection.fat }} | एसएनएफ: {{ collection.snf }}\n\n"
                    "गुणवत्ता और निरंतरता बनाए रखने के लिए धन्यवाद।\n"
                    "- {{ site_name }} डेयरी प्रबंधन प्रणाली"
                ),
                "email_subject_template": "दूध संग्रह पुष्टि – {{ collection.collection_date|date:'d M Y' }}",
                "email_body_template": (
                    "नमस्ते {{ recipient.first_name }},\n\n"
                    "आपके दूध संग्रह विवरण {{ site_name }} में सफलतापूर्वक दर्ज किए गए हैं।\n\n"
                    "**संग्रह विवरण:**\n"
                    "- सदस्य कोड: {{ collection.member_code }}\n"
                    "- तिथि: {{ collection.collection_date|date:'d M Y, H:i' }}\n"
                    "- शिफ्ट: {{ collection.shift_code }}\n"
                    "- मात्रा: {{ collection.qty }} लीटर\n"
                    "- वसा: {{ collection.fat }} | एसएनएफ: {{ collection.snf }}\n\n"
                    "किसी भी विसंगति के लिए, कृपया अपने संग्रह केंद्र से संपर्क करें।\n\n"
                    "सादर,\n"
                    "{{ site_name }} टीम"
                ),
                "route_template": "/",
                "category": "mpp_collection",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.PUSH,
                    NotificationChannel.EMAIL,
                ],
            },
            # Feedback Update - English
            {
                "name": "feedback_update_en",
                "locale": "en",
                "title_template": "Your Feedback Update: {{ site_name }}",
                "body_template": (
                    "Hello {{ recipient.first_name }},\n\n"
                    "There has been an update on your feedback (ID: {{ feedback.feedback_id }}):\n\n"
                    "- Status: {{ feedback.status|capfirst }}\n"
                    "{% if feedback.assigned_to %}- Assigned To: {{ feedback.assigned_to.get_full_name }}{% endif %}\n"
                    "{% if feedback.resolved_at %}- Resolved At: {{ feedback.resolved_at|date:'d M Y, H:i' }}{% endif %}\n"
                    "\nMessage:\n{{ feedback.message|truncatechars:200 }}\n\n"
                    "You can view full details in your profile.\n"
                    "- {{ site_name }} Team"
                ),
                "email_subject_template": "Feedback Update – {{ feedback.feedback_id }}",
                "email_body_template": (
                    "Hello {{ recipient.first_name }},\n\n"
                    "Your feedback (ID: {{ feedback.feedback_id }}) has been updated.\n\n"
                    "Details:\n"
                    "- Status: {{ feedback.status|capfirst }}\n"
                    "{% if feedback.assigned_to %}- Assigned To: {{ feedback.assigned_to.get_full_name }}{% endif %}\n"
                    "{% if feedback.resolved_at %}- Resolved At: {{ feedback.resolved_at|date:'d M Y, H:i' }}{% endif %}\n"
                    "\nFeedback Message:\n{{ feedback.message }}\n\n"
                    "Please check the app for full details and updates.\n\n"
                    "Regards,\n"
                    "{{ site_name }} Team"
                ),
                "route_template": "feedback",
                "category": "feedback",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.PUSH,
                    NotificationChannel.EMAIL,
                ],
            },
            # Feedback Update - Hindi
            {
                "name": "feedback_update_hi",
                "locale": "hi",
                "title_template": "आपकी फीडबैक अपडेट: {{ site_name }}",
                "body_template": (
                    "नमस्ते {{ recipient.first_name }},\n\n"
                    "आपकी फीडबैक (आईडी: {{ feedback.feedback_id }}) में अपडेट हुआ है:\n\n"
                    "- स्थिति: {{ feedback.status|capfirst }}\n"
                    "{% if feedback.assigned_to %}- सौंपा गया: {{ feedback.assigned_to.get_full_name }}{% endif %}\n"
                    "{% if feedback.resolved_at %}- समाधान समय: {{ feedback.resolved_at|date:'d M Y, H:i' }}{% endif %}\n"
                    "\nसंदेश:\n{{ feedback.message|truncatechars:200 }}\n\n"
                    "आप अपनी प्रोफाइल में पूर्ण विवरण देख सकते हैं।\n"
                    "- {{ site_name }} टीम"
                ),
                "email_subject_template": "फीडबैक अपडेट – {{ feedback.feedback_id }}",
                "email_body_template": (
                    "नमस्ते {{ recipient.first_name }},\n\n"
                    "आपकी फीडबैक (आईडी: {{ feedback.feedback_id }}) अपडेट की गई है।\n\n"
                    "विवरण:\n"
                    "- स्थिति: {{ feedback.status|capfirst }}\n"
                    "{% if feedback.assigned_to %}- सौंपा गया: {{ feedback.assigned_to.get_full_name }}{% endif %}\n"
                    "{% if feedback.resolved_at %}- समाधान समय: {{ feedback.resolved_at|date:'d M Y, H:i' }}{% endif %}\n"
                    "\nफीडबैक संदेश:\n{{ feedback.message }}\n\n"
                    "कृपया पूर्ण विवरण और अपडेट के लिए ऐप देखें।\n\n"
                    "सादर,\n"
                    "{{ site_name }} टीम"
                ),
                "route_template": "feedback",
                "category": "feedback",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.PUSH,
                    NotificationChannel.EMAIL,
                ],
            },
            {
                "name": "feedback_status_change_hi",
                "locale": "hi",
                "title_template": "फीडबैक स्थिति अपडेट – {{ feedback.feedback_id }}",
                "body_template": (
                    "नमस्ते {{ recipient.first_name }},\n\n"
                    "आपकी फीडबैक (आईडी: {{ feedback.feedback_id }}) की स्थिति बदल गई है:\n\n"
                    "- पुरानी स्थिति: {{ old_status|capfirst }}\n"
                    "- नई स्थिति: {{ new_status|capfirst }}\n"
                    "{% if feedback.assigned_to %}- जिम्मेदार: {{ feedback.assigned_to.get_full_name }}{% endif %}\n"
                    "{% if feedback.resolved_at %}- समाधान समय: {{ feedback.resolved_at|date:'d M Y, H:i' }}{% endif %}\n"
                    "\nआप ऐप में जाकर विस्तृत जानकारी देख सकते हैं।\n\n"
                    "- {{ site_name }} टीम"
                ),
                "email_subject_template": "फीडबैक स्थिति अपडेट – {{ feedback.feedback_id }}",
                "email_body_template": (
                    "प्रिय {{ recipient.first_name }},\n\n"
                    "आपकी फीडबैक (आईडी: {{ feedback.feedback_id }}) की स्थिति अपडेट की गई है।\n\n"
                    "विवरण:\n"
                    "- पुरानी स्थिति: {{ old_status|capfirst }}\n"
                    "- नई स्थिति: {{ new_status|capfirst }}\n"
                    "{% if feedback.assigned_to %}- जिम्मेदार व्यक्ति: {{ feedback.assigned_to.get_full_name }}{% endif %}\n"
                    "{% if feedback.resolved_at %}- समाधान समय: {{ feedback.resolved_at|date:'d M Y, H:i' }}{% endif %}\n"
                    "\nकृपया पूर्ण विवरण और आगे की जानकारी के लिए ऐप देखें।\n\n"
                    "सादर,\n"
                    "{{ site_name }} टीम"
                ),
                "route_template": "/feedback/{{ feedback.feedback_id }}/",
                "category": "feedback",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.PUSH,
                    NotificationChannel.EMAIL,
                ],
            },
            {
                "name": "feedback_status_change_en",
                "locale": "en",
                "title_template": "Feedback Status Updated – {{ feedback.feedback_id }}",
                "body_template": (
                    "Hello {{ recipient.first_name }},\n\n"
                    "Your feedback (ID: {{ feedback.feedback_id }}) status has been updated.\n\n"
                    "- Previous Status: {{ old_status|capfirst }}\n"
                    "- New Status: {{ new_status|capfirst }}\n"
                    "{% if feedback.assigned_to %}- Assigned To: {{ feedback.assigned_to.get_full_name }}{% endif %}\n"
                    "{% if feedback.resolved_at %}- Resolved At: {{ feedback.resolved_at|date:'d M Y, H:i' }}{% endif %}\n"
                    "\nYou can view complete details in your app.\n\n"
                    "- The {{ site_name }} Team"
                ),
                "email_subject_template": "Feedback Status Updated – {{ feedback.feedback_id }}",
                "email_body_template": (
                    "Dear {{ recipient.first_name }},\n\n"
                    "Your feedback (ID: {{ feedback.feedback_id }}) status has changed.\n\n"
                    "Details:\n"
                    "- Previous Status: {{ old_status|capfirst }}\n"
                    "- New Status: {{ new_status|capfirst }}\n"
                    "{% if feedback.assigned_to %}- Assigned To: {{ feedback.assigned_to.get_full_name }}{% endif %}\n"
                    "{% if feedback.resolved_at %}- Resolved At: {{ feedback.resolved_at|date:'d M Y, H:i' }}{% endif %}\n"
                    "\nPlease check the app for full details and updates.\n\n"
                    "Regards,\n"
                    "The {{ site_name }} Team"
                ),
                "route_template": "/feedback/{{ feedback.feedback_id }}/",
                "category": "feedback",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.PUSH,
                    NotificationChannel.EMAIL,
                ],
            },
            # Sahayak Incentive - English
            {
                "name": "sahayak_incentive_update_en",
                "locale": "en",
                "title_template": "Your Incentive Details: {{ site_name }}",
                "body_template": (
                    "Hello {{ recipient.first_name }},\n\n"
                    "Your incentive for {{ incentive.month }}/{{ incentive.year }} has been calculated:\n\n"
                    "- Milk Quantity: {{ incentive.milk_qty }} L\n"
                    "- Milk Incentive: ₹{{ incentive.milk_incentive }}\n"
                    "- Cattle Feed Incentive: ₹{{ incentive.cf_incentive }}\n"
                    "- Mineral Mixture Incentive: ₹{{ incentive.mm_incentive }}\n"
                    "- Other Incentives: ₹{{ incentive.other_incentive }}\n"
                    "- TDS Deduction: ₹{{ incentive.tds_amt }}\n"
                    "- Payable Amount: ₹{{ incentive.payable }}\n"
                    "- Closing Balance: ₹{{ incentive.closing }}\n\n"
                    "Please check the app for full details and history.\n\n"
                    "Regards,\n"
                    "{{ site_name }} Team"
                ),
                "email_subject_template": "Incentive Update – {{ incentive.month }}/{{ incentive.year }}",
                "email_body_template": (
                    "Hello {{ recipient.first_name }},\n\n"
                    "Your incentive for {{ incentive.month }}/{{ incentive.year }} has been calculated:\n\n"
                    "- Milk Quantity: {{ incentive.milk_qty }} L\n"
                    "- Milk Incentive: ₹{{ incentive.milk_incentive }}\n"
                    "- Cattle Feed Incentive: ₹{{ incentive.cf_incentive }}\n"
                    "- Mineral Mixture Incentive: ₹{{ incentive.mm_incentive }}\n"
                    "- Other Incentives: ₹{{ incentive.other_incentive }}\n"
                    "- TDS Deduction: ₹{{ incentive.tds_amt }}\n"
                    "- Payable Amount: ₹{{ incentive.payable }}\n"
                    "- Closing Balance: ₹{{ incentive.closing }}\n\n"
                    "Check the app for full details.\n\n"
                    "Regards,\n"
                    "{{ site_name }} Team"
                ),
                "route_template": "/incentive/?year={{ incentive.year }}&month={{ incentive.month }}",
                "category": "incentive",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.PUSH,
                    NotificationChannel.EMAIL,
                ],
            },
            # Sahayak Incentive - Hindi
            {
                "name": "sahayak_incentive_update_hi",
                "locale": "hi",
                "title_template": "आपका प्रोत्साहन विवरण: {{ site_name }}",
                "body_template": (
                    "नमस्ते {{ recipient.first_name }},\n\n"
                    "{{ incentive.month }}/{{ incentive.year }} के लिए आपका प्रोत्साहन गणना किया गया है:\n\n"
                    "- दूध की मात्रा: {{ incentive.milk_qty }} लीटर\n"
                    "- दूध प्रोत्साहन: ₹{{ incentive.milk_incentive }}\n"
                    "- पशु आहार प्रोत्साहन: ₹{{ incentive.cf_incentive }}\n"
                    "- खनिज मिश्रण प्रोत्साहन: ₹{{ incentive.mm_incentive }}\n"
                    "- अन्य प्रोत्साहन: ₹{{ incentive.other_incentive }}\n"
                    "- टीडीएस कटौती: ₹{{ incentive.tds_amt }}\n"
                    "- देय राशि: ₹{{ incentive.payable }}\n"
                    "- समापन शेष: ₹{{ incentive.closing }}\n\n"
                    "पूर्ण विवरण और इतिहास के लिए कृपया ऐप देखें।\n\n"
                    "सादर,\n"
                    "{{ site_name }} टीम"
                ),
                "email_subject_template": "प्रोत्साहन अपडेट – {{ incentive.month }}/{{ incentive.year }}",
                "email_body_template": (
                    "नमस्ते {{ recipient.first_name }},\n\n"
                    "{{ incentive.month }}/{{ incentive.year }} के लिए आपका प्रोत्साहन गणना किया गया है:\n\n"
                    "- दूध की मात्रा: {{ incentive.milk_qty }} लीटर\n"
                    "- दूध प्रोत्साहन: ₹{{ incentive.milk_incentive }}\n"
                    "- पशु आहार प्रोत्साहन: ₹{{ incentive.cf_incentive }}\n"
                    "- खनिज मिश्रण प्रोत्साहन: ₹{{ incentive.mm_incentive }}\n"
                    "- अन्य प्रोत्साहन: ₹{{ incentive.other_incentive }}\n"
                    "- टीडीएस कटौती: ₹{{ incentive.tds_amt }}\n"
                    "- देय राशि: ₹{{ incentive.payable }}\n"
                    "- समापन शेष: ₹{{ incentive.closing }}\n\n"
                    "पूर्ण विवरण के लिए ऐप देखें।\n\n"
                    "सादर,\n"
                    "{{ site_name }} टीम"
                ),
                "route_template": "/incentive/?year={{ incentive.year }}&month={{ incentive.month }}",
                "category": "incentive",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.PUSH,
                    NotificationChannel.EMAIL,
                ],
            },
            # News Published - English
            {
                "name": "news_published_en",
                "locale": "en",
                "title_template": "New Article Published: {{ news.title }}",
                "body_template": (
                    "Hello {{ recipient.first_name }},\n\n"
                    "A new news article has been published in {{ site_name }}:\n\n"
                    "- Title: {{ news.title }}\n"
                    "- Summary: {{ news.summary|truncatechars:150 }}\n"
                    "- Author: {{ news.author }}\n"
                    "- Published On: {{ news.published_date|date:'d M Y, H:i' }}\n\n"
                    "Click to read the full article and stay updated.\n\n"
                    "- {{ site_name }} Team"
                ),
                "email_subject_template": "New News Article – {{ news.title }}",
                "email_body_template": (
                    "Hello {{ recipient.first_name }},\n\n"
                    "A new news article has been published:\n\n"
                    "- Title: {{ news.title }}\n"
                    "- Summary: {{ news.summary }}\n"
                    "- Author: {{ news.author }}\n"
                    "- Published On: {{ news.published_date|date:'d M Y, H:i' }}\n\n"
                    "You can view the full article in the app.\n\n"
                    "Regards,\n"
                    "{{ site_name }} Team"
                ),
                "route_template": "/news/{{ news.slug }}/",
                "category": "news",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.PUSH,
                    NotificationChannel.EMAIL,
                ],
            },
            # News Published - Hindi``
            {
                "name": "news_published_hi",
                "locale": "hi",
                "title_template": "नया लेख प्रकाशित: {{ news.title }}",
                "body_template": (
                    "नमस्ते {{ recipient.first_name }},\n\n"
                    "{{ site_name }} में एक नया समाचार लेख प्रकाशित किया गया है:\n\n"
                    "- शीर्षक: {{ news.title }}\n"
                    "- सारांश: {{ news.summary|truncatechars:150 }}\n"
                    "- लेखक: {{ news.author }}\n"
                    "- प्रकाशन तिथि: {{ news.published_date|date:'d M Y, H:i' }}\n\n"
                    "पूरा लेख पढ़ने और अपडेट रहने के लिए क्लिक करें।\n\n"
                    "- {{ site_name }} टीम"
                ),
                "email_subject_template": "नया समाचार लेख – {{ news.title }}",
                "email_body_template": (
                    "नमस्ते {{ recipient.first_name }},\n\n"
                    "एक नया समाचार लेख प्रकाशित किया गया है:\n\n"
                    "- शीर्षक: {{ news.title }}\n"
                    "- सारांश: {{ news.summary }}\n"
                    "- लेखक: {{ news.author }}\n"
                    "- प्रकाशन तिथि: {{ news.published_date|date:'d M Y, H:i' }}\n\n"
                    "आप ऐप में पूरा लेख देख सकते हैं।\n\n"
                    "सादर,\n"
                    "{{ site_name }} टीम"
                ),
                "route_template": "/news/{{ news.slug }}/",
                "category": "news",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.PUSH,
                    NotificationChannel.EMAIL,
                ],
            },
            # Order Created - English
            {
                "name": "order_created_en",
                "locale": "en",
                "title_template": "Order Confirmed #{{ object.order_number }}",
                "body_template": "Your order has been confirmed and is being processed.",
                "route_template": "/orders/{{ object_id }}/",
                "url_name": "orders:detail",
                "category": "orders",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.EMAIL,
                    NotificationChannel.PUSH,
                ],
            },
            # Order Created - Hindi
            {
                "name": "order_created_hi",
                "locale": "hi",
                "title_template": "ऑर्डर की पुष्टि #{{ object.order_number }}",
                "body_template": "आपका ऑर्डर की पुष्टि हो गई है और प्रक्रिया में है।",
                "route_template": "/orders/{{ object_id }}/",
                "url_name": "orders:detail",
                "category": "orders",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.EMAIL,
                    NotificationChannel.PUSH,
                ],
            },
            # Order Shipped - English
            {
                "name": "order_shipped_en",
                "locale": "en",
                "title_template": "Order Shipped #{{ object.order_number }}",
                "body_template": "Your order has been shipped! Track: {{ tracking_code }}",
                "route_template": "/orders/{{ object_id }}/track/",
                "category": "orders",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.EMAIL,
                    NotificationChannel.PUSH,
                    NotificationChannel.SMS,
                ],
            },
            # Order Shipped - Hindi
            {
                "name": "order_shipped_hi",
                "locale": "hi",
                "title_template": "ऑर्डर भेज दिया गया #{{ object.order_number }}",
                "body_template": "आपका ऑर्डर भेज दिया गया है! ट्रैक करें: {{ tracking_code }}",
                "route_template": "/orders/{{ object_id }}/track/",
                "category": "orders",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.EMAIL,
                    NotificationChannel.PUSH,
                    NotificationChannel.SMS,
                ],
            },
            # Payment Received - English
            {
                "name": "payment_received_en",
                "locale": "en",
                "title_template": "Payment Received",
                "body_template": "We have received your payment of ${{ amount }}",
                "route_template": "/payments/{{ object_id }}/",
                "category": "payments",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.EMAIL,
                ],
            },
            # Payment Received - Hindi
            {
                "name": "payment_received_hi",
                "locale": "hi",
                "title_template": "भुगतान प्राप्त हुआ",
                "body_template": "हमें आपका ${{ amount }} का भुगतान प्राप्त हुआ है",
                "route_template": "/payments/{{ object_id }}/",
                "category": "payments",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.EMAIL,
                ],
            },
            # System Maintenance - English
            {
                "name": "system_maintenance_en",
                "locale": "en",
                "title_template": "System Maintenance Scheduled",
                "body_template": "System maintenance is scheduled for {{ maintenance_date }}",
                "route_template": "/system/maintenance/",
                "category": "system",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.EMAIL,
                    NotificationChannel.PUSH,
                ],
            },
            # System Maintenance - Hindi
            {
                "name": "system_maintenance_hi",
                "locale": "hi",
                "title_template": "सिस्टम रखरखाव निर्धारित",
                "body_template": "{{ maintenance_date }} के लिए सिस्टम रखरखाव निर्धारित है",
                "route_template": "/system/maintenance/",
                "category": "system",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.EMAIL,
                    NotificationChannel.PUSH,
                ],
            },
            # Security Alert - English
            {
                "name": "security_alert_en",
                "locale": "en",
                "title_template": "Security Alert",
                "body_template": "Unusual activity detected on your account",
                "route_template": "/security/alerts/",
                "category": "security",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.EMAIL,
                    NotificationChannel.PUSH,
                    NotificationChannel.SMS,
                ],
            },
            # Security Alert - Hindi
            {
                "name": "security_alert_hi",
                "locale": "hi",
                "title_template": "सुरक्षा अलर्ट",
                "body_template": "आपके खाते पर असामान्य गतिविधि का पता चला है",
                "route_template": "/security/alerts/",
                "category": "security",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.EMAIL,
                    NotificationChannel.PUSH,
                    NotificationChannel.SMS,
                ],
            },
            {
                "name": "member_sync_completed",
                "locale": "en",
                "title_template": "Member Data Synchronization Completed Successfully",
                "body_template": (
                    "Hello {{ recipient.first_name }},\n\n"
                    "The member data synchronization task has been completed successfully.\n\n"
                    "- Source: MemberHierarchyView (MSSQL)\n"
                    "- Destination: MembersMasterCopy (PostgreSQL)\n"
                    "- Records Created: {{ collection.created }}\n"
                    "- Records Updated: {{ collection.updated }}\n\n"
                    "You can review the updated data in the Admin Panel.\n\n"
                    "- {{ site_name }} System"
                ),
                "email_subject_template": "Member Synchronization Completed – {{ site_name }}",
                "email_body_template": (
                    "Dear {{ recipient.first_name }},\n\n"
                    "The member data synchronization process has been completed.\n\n"
                    "Summary:\n"
                    "- Records Created: {{ collection.created }}\n"
                    "- Records Updated: {{ collection.updated }}\n"
                    "- Time: {{ collection.timestamp|date:'d M Y, H:i' }}\n\n"
                    "For detailed information, please check the Admin Dashboard.\n\n"
                    "Regards,\n"
                    "{{ site_name }} System"
                ),
                "route_template": "/admin/veterinary/membersmastercopy/",
                "category": "data_sync",
                "enabled_channels": [
                    NotificationChannel.IN_APP,
                    NotificationChannel.PUSH,
                    NotificationChannel.EMAIL,
                ],
            },
        ]

        app_filter = options.get("app")
        locale_filter = options.get("locale")

        if app_filter:
            templates = [t for t in templates if t["category"] == app_filter]

        if locale_filter:
            templates = [t for t in templates if t["locale"] == locale_filter]

        created_count = 0
        updated_count = 0

        for template_data in templates:
            # Use name + locale as unique identifier
            template, created = NotificationTemplate.objects.get_or_create(
                name=template_data["name"],
                locale=template_data["locale"],
                defaults=template_data,
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created template: {template.name} ({template.locale})"
                    )
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(
                        f"Template already exists: {template.name} ({template.locale})"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nCreated {created_count} new templates, {updated_count} already existed"
            )
        )


# class Command(BaseCommand):
#     help = "Create default notification templates"

#     def add_arguments(self, parser):
#         parser.add_argument("--app", type=str, help="Create templates for specific app")

#     def handle(self, *args, **options):
#         templates = [
#             {
#                 "name": "mpp_collection_created",
#                 "title_template": "New Milk Collection Recorded: {{ site_name }}",
#                 "body_template": (
#                     "Dear {{ recipient.first_name }},\n\n"
#                     "A new milk collection entry has been successfully recorded for Member Code {{ collection.member_code }} "
#                     "on {{ collection.collection_date|date:'d M Y, H:i' }} during {{ collection.shift_code }} shift.\n"
#                     "Quantity: {{ collection.qty }} L | Fat: {{ collection.fat }} | SNF: {{ collection.snf }}\n\n"
#                     "Thank you for maintaining quality and consistency.\n"
#                     "- {{ site_name }} Dairy Management System"
#                 ),
#                 "email_subject_template": "Milk Collection Confirmation – {{ collection.collection_date|date:'d M Y' }}",
#                 "email_body_template": (
#                     "Hello {{ recipient.first_name }},\n\n"
#                     "Your milk collection details have been successfully recorded in {{ site_name }}.\n\n"
#                     "**Collection Details:**\n"
#                     "- Member Code: {{ collection.member_code }}\n"
#                     "- Date: {{ collection.collection_date|date:'d M Y, H:i' }}\n"
#                     "- Shift: {{ collection.shift_code }}\n"
#                     "- Quantity: {{ collection.qty }} L\n"
#                     "- Fat: {{ collection.fat }} | SNF: {{ collection.snf }}\n\n"
#                     "For any discrepancies, please contact your collection center.\n\n"
#                     "Warm regards,\n"
#                     "{{ site_name }} Team"
#                 ),
#                 "route_template": "/collections/{{ collection.mpp_collection_code }}/details/",
#                 "category": "mpp_collection",
#                 "enabled_channels": [
#                     NotificationChannel.IN_APP,
#                     NotificationChannel.PUSH,
#                     NotificationChannel.EMAIL,
#                 ],
#             },
#             {
#                 "name": "feedback_update",
#                 "title_template": "Your Feedback Update: {{ site_name }}",
#                 "body_template": (
#                     "Hello {{ recipient.first_name }},\n\n"
#                     "There has been an update on your feedback (ID: {{ feedback.feedback_id }}):\n\n"
#                     "- Status: {{ feedback.status|capfirst }}\n"
#                     "{% if feedback.assigned_to %}- Assigned To: {{ feedback.assigned_to.get_full_name }}{% endif %}\n"
#                     "{% if feedback.resolved_at %}- Resolved At: {{ feedback.resolved_at|date:'d M Y, H:i' }}{% endif %}\n"
#                     "\nMessage:\n{{ feedback.message|truncatechars:200 }}\n\n"
#                     "You can view full details in your profile.\n"
#                     "- {{ site_name }} Team"
#                 ),
#                 "email_subject_template": "Feedback Update – {{ feedback.feedback_id }}",
#                 "email_body_template": (
#                     "Hello {{ recipient.first_name }},\n\n"
#                     "Your feedback (ID: {{ feedback.feedback_id }}) has been updated.\n\n"
#                     "Details:\n"
#                     "- Status: {{ feedback.status|capfirst }}\n"
#                     "{% if feedback.assigned_to %}- Assigned To: {{ feedback.assigned_to.get_full_name }}{% endif %}\n"
#                     "{% if feedback.resolved_at %}- Resolved At: {{ feedback.resolved_at|date:'d M Y, H:i' }}{% endif %}\n"
#                     "\nFeedback Message:\n{{ feedback.message }}\n\n"
#                     "Please check the app for full details and updates.\n\n"
#                     "Regards,\n"
#                     "{{ site_name }} Team"
#                 ),
#                 "route_template": "/feedback/{{ feedback.feedback_id }}/details/",
#                 "category": "feedback",
#                 "enabled_channels": [
#                     NotificationChannel.IN_APP,
#                     NotificationChannel.PUSH,
#                     NotificationChannel.EMAIL,
#                 ],
#             },
#             {
#                 "name": "sahayak_incentive_update",
#                 "title_template": "Your Incentive Details: {{ site_name }}",
#                 "body_template": (
#                     "Hello {{ recipient.first_name }},\n\n"
#                     "Your incentive for {{ incentive.month }}/{{ incentive.year }} has been calculated:\n\n"
#                     "- Milk Quantity: {{ incentive.milk_qty }} L\n"
#                     "- Milk Incentive: ₹{{ incentive.milk_incentive }}\n"
#                     "- Cattle Feed Incentive: ₹{{ incentive.cf_incentive }}\n"
#                     "- Mineral Mixture Incentive: ₹{{ incentive.mm_incentive }}\n"
#                     "- Other Incentives: ₹{{ incentive.other_incentive }}\n"
#                     "- TDS Deduction: ₹{{ incentive.tds_amt }}\n"
#                     "- Payable Amount: ₹{{ incentive.payable }}\n"
#                     "- Closing Balance: ₹{{ incentive.closing }}\n\n"
#                     "Please check the app for full details and history.\n\n"
#                     "Regards,\n"
#                     "{{ site_name }} Team"
#                 ),
#                 "email_subject_template": "Incentive Update – {{ incentive.month }}/{{ incentive.year }}",
#                 "email_body_template": (
#                     "Hello {{ recipient.first_name }},\n\n"
#                     "Your incentive for {{ incentive.month }}/{{ incentive.year }} has been calculated:\n\n"
#                     "- Milk Quantity: {{ incentive.milk_qty }} L\n"
#                     "- Milk Incentive: ₹{{ incentive.milk_incentive }}\n"
#                     "- Cattle Feed Incentive: ₹{{ incentive.cf_incentive }}\n"
#                     "- Mineral Mixture Incentive: ₹{{ incentive.mm_incentive }}\n"
#                     "- Other Incentives: ₹{{ incentive.other_incentive }}\n"
#                     "- TDS Deduction: ₹{{ incentive.tds_amt }}\n"
#                     "- Payable Amount: ₹{{ incentive.payable }}\n"
#                     "- Closing Balance: ₹{{ incentive.closing }}\n\n"
#                     "Check the app for full details.\n\n"
#                     "Regards,\n"
#                     "{{ site_name }} Team"
#                 ),
#                 "route_template": "/incentives/{{ incentive.year }}/{{ incentive.month }}/",
#                 "category": "incentive",
#                 "enabled_channels": [
#                     NotificationChannel.IN_APP,
#                     NotificationChannel.PUSH,
#                     NotificationChannel.EMAIL,
#                 ],
#             },
#             {
#                 "name": "news_published",
#                 "title_template": "New Article Published: {{ news.title }}",
#                 "body_template": (
#                     "Hello {{ recipient.first_name }},\n\n"
#                     "A new news article has been published in {{ site_name }}:\n\n"
#                     "- Title: {{ news.title }}\n"
#                     "- Summary: {{ news.summary|truncatechars:150 }}\n"
#                     "- Author: {{ news.author }}\n"
#                     "- Published On: {{ news.published_date|date:'d M Y, H:i' }}\n\n"
#                     "Click to read the full article and stay updated.\n\n"
#                     "- {{ site_name }} Team"
#                 ),
#                 "email_subject_template": "New News Article – {{ news.title }}",
#                 "email_body_template": (
#                     "Hello {{ recipient.first_name }},\n\n"
#                     "A new news article has been published:\n\n"
#                     "- Title: {{ news.title }}\n"
#                     "- Summary: {{ news.summary }}\n"
#                     "- Author: {{ news.author }}\n"
#                     "- Published On: {{ news.published_date|date:'d M Y, H:i' }}\n\n"
#                     "You can view the full article in the app.\n\n"
#                     "Regards,\n"
#                     "{{ site_name }} Team"
#                 ),
#                 "route_template": "/news/{{ news.slug }}/",
#                 "category": "news",
#                 "enabled_channels": [
#                     NotificationChannel.IN_APP,
#                     NotificationChannel.PUSH,
#                     NotificationChannel.EMAIL,
#                 ],
#             },

#             {
#                 "name": "order_created",
#                 "title_template": "Order Confirmed #{{ object.order_number }}",
#                 "body_template": "Your order has been confirmed and is being processed.",
#                 "route_template": "/orders/{{ object_id }}/",
#                 "url_name": "orders:detail",
#                 "category": "orders",
#                 "enabled_channels": [
#                     NotificationChannel.IN_APP,
#                     NotificationChannel.EMAIL,
#                     NotificationChannel.PUSH,
#                 ],
#             },
#             {
#                 "name": "order_shipped",
#                 "title_template": "Order Shipped #{{ object.order_number }}",
#                 "body_template": "Your order has been shipped! Track: {{ tracking_code }}",
#                 "route_template": "/orders/{{ object_id }}/track/",
#                 "category": "orders",
#                 "enabled_channels": [
#                     NotificationChannel.IN_APP,
#                     NotificationChannel.EMAIL,
#                     NotificationChannel.PUSH,
#                     NotificationChannel.SMS,
#                 ],
#             },
#             {
#                 "name": "payment_received",
#                 "title_template": "Payment Received",
#                 "body_template": "We have received your payment of ${{ amount }}",
#                 "route_template": "/payments/{{ object_id }}/",
#                 "category": "payments",
#                 "enabled_channels": [
#                     NotificationChannel.IN_APP,
#                     NotificationChannel.EMAIL,
#                 ],
#             },
#             # System templates
#             {
#                 "name": "system_maintenance",
#                 "title_template": "System Maintenance Scheduled",
#                 "body_template": "System maintenance is scheduled for {{ maintenance_date }}",
#                 "route_template": "/system/maintenance/",
#                 "category": "system",
#                 "enabled_channels": [
#                     NotificationChannel.IN_APP,
#                     NotificationChannel.EMAIL,
#                     NotificationChannel.PUSH,
#                 ],
#             },
#             {
#                 "name": "security_alert",
#                 "title_template": "Security Alert",
#                 "body_template": "Unusual activity detected on your account",
#                 "route_template": "/security/alerts/",
#                 "category": "security",
#                 "enabled_channels": [
#                     NotificationChannel.IN_APP,
#                     NotificationChannel.EMAIL,
#                     NotificationChannel.PUSH,
#                     NotificationChannel.SMS,
#                 ],
#             },
#         ]

#         app_filter = options.get("app")
#         if app_filter:
#             templates = [t for t in templates if t["category"] == app_filter]

#         created_count = 0
#         for template_data in templates:
#             template, created = NotificationTemplate.objects.get_or_create(
#                 name=template_data["name"], defaults=template_data
#             )

#             if created:
#                 created_count += 1
#                 self.stdout.write(
#                     self.style.SUCCESS(f"Created template: {template.name}")
#                 )
#             else:
#                 self.stdout.write(
#                     self.style.WARNING(f"Template already exists: {template.name}")
#                 )

#         self.stdout.write(
#             self.style.SUCCESS(f"\nCreated {created_count} new templates")
#         )
