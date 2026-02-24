from tortoise import fields, models


class Lead(models.Model):
    id = fields.IntField(pk=True)

    source = fields.CharField(max_length=50)
    stage = fields.CharField(max_length=50, default="new")
    business_domain = fields.CharField(max_length=100, null=True)

    activity_count = fields.IntField(default=0)

    ai_score = fields.FloatField(null=True)
    ai_recommendation = fields.CharField(max_length=50, null=True)
    ai_reason = fields.TextField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "leads"
