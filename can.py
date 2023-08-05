ALL_SKILLS = {
    'sbj': 'Spring Ball Jump',
    # 'sbj2': 'Double Spring Ball Jump',
    # 'sbj3': 'Triple Spring Ball Jump',
    'hellrun': 'Hell Run',
    'suitless': 'Suitless',
    'ibj': 'Infinite Bomb Jump',
    'gravityJump': 'Gravity Jump',
    'storeSpark': 'Store Shine Spark',
    'shortCharge1': 'Short Charge (1-tap)',
    'shortCharge2': 'Short Charge (2-tap)',
    # 'shortCharge3': 'Short Charge (3-tap)',
    # 'shortCharge4': 'Short Charge (4-tap)',
}

class Can:
    def __str__(self):
        return 'Can:' + '|'.join([key for key in ALL_SKILLS if getattr(self, key)])
    def __init__(self, skills):
        for skill in ALL_SKILLS:
            setattr(self, skill, False)
        for skill in skills:
            if not skill in ALL_SKILLS:
                raise ValueError(f'Unknown skill: {skill}')
            setattr(self, skill, True)
