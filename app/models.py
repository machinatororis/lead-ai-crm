from tortoise import fields, models


class Lead(models.Model):
    """
    Лид в холодной стадии.
    Этапы: new -> contacted -> qualified -> transferred / lost
    """

    id = fields.IntField(pk=True)

    source = fields.CharField(max_length=50)  # scanner / partner / manual
    stage = fields.CharField(max_length=50, default="new")  # new, contacted, ...

    business_domain = fields.CharField(
        max_length=100,
        null=True,  # может быть неизвестен
    )

    activity_count = fields.IntField(default=0)

    ai_score = fields.FloatField(null=True)
    ai_recommendation = fields.CharField(max_length=50, null=True)
    ai_reason = fields.TextField(null=True)

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "leads"

    def __str__(self) -> str:
        return f"Lead(id={self.id}, stage={self.stage})"


class Sale(models.Model):
    """
    Продажа, которая создаётся при переводе лида в продажи.
    Этапы: new -> kyc -> agreement -> paid / lost
    """

    id = fields.IntField(pk=True)

    lead: fields.OneToOneRelation[Lead] = fields.OneToOneField(
        "models.Lead",
        related_name="sale",
        on_delete=fields.CASCADE,
    )

    stage = fields.CharField(max_length=50, default="new")  # new, kyc, agreement...

    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "sales"

    def __str__(self) -> str:
        return f"Sale(id={self.id}, lead_id={self.lead_id}, stage={self.stage})"
