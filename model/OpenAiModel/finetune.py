from openai import OpenAI
client = OpenAI()







# Code here for file upload (fine-tuning purpose)



class finetune(object):
    def __init__(self,training_file,model):
        super().__init__()
        self.training_file = training_file
        self.model = model

    def create_finetune(self):
        response = client.fine_tuning.jobs.create(
            training_file=self.training_file,
            model=self.model
        )

        return response

