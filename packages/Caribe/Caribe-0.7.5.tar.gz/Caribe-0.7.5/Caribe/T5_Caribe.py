#Author: Keston Smith

from transformers import AutoTokenizer
from datasets import load_dataset
from transformers import AutoModelForSeq2SeqLM, Seq2SeqTrainingArguments, Seq2SeqTrainer, DataCollatorForSeq2Seq

tokenizer = AutoTokenizer.from_pretrained("t5-base")
class T5_Trainer:

  def __init__(self, train_dataset_path:str, eval_dataset_path:str):
      self.model_name = "t5-base"
      self.train_dataset_path = train_dataset_path
      self.eval_dataset_path = eval_dataset_path
        
      if (not open(self.train_dataset_path) or  not open(self.eval_dataset_path)):
          raise FileNotFoundError
      
  def connect_datasets(self, format):
      self.format=format
      self.dataset = load_dataset(self.format, data_files={"train":self.train_dataset_path}, delimiter=",")
      self.dataset1 = load_dataset(self.format, data_files={"test":self.eval_dataset_path}, delimiter=",")

  def caribe_preprocessor(self, examples):
      self.examples=examples
      model_inputs = tokenizer(self.examples["input"], max_length=512, truncation=True)
      with tokenizer.as_target_tokenizer():   
          labels = tokenizer(self.examples["target"], max_length=512, truncation=True)
      model_inputs["labels"] = labels["input_ids"]
      return model_inputs


  def caribe_training(self, output_path:str, epochs:int, eval_strategy:str, l_rate, train_batch_size:int, eval_batch_size:int, decay:float, checkpoints:int):
      self.model = AutoModelForSeq2SeqLM.from_pretrained("t5-base")
      self.data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=self.model)
      
      caribe_training_args = Seq2SeqTrainingArguments(
      output_dir=output_path,
      evaluation_strategy=eval_strategy,
      learning_rate=l_rate,
      per_device_train_batch_size=train_batch_size,
      per_device_eval_batch_size=eval_batch_size,
      weight_decay=decay,
      save_total_limit=checkpoints,
      num_train_epochs=epochs,)
      
      trainer = Seq2SeqTrainer(
      model=self.model,
      args=caribe_training_args,
      train_dataset=self.dataset.map(self.caribe_preprocessor, batched=True, remove_columns=["input", "target"],)['train'],
      eval_dataset=self.dataset1.map(self.caribe_preprocessor, batched=True, remove_columns=["input", "target"],)['test'],
      tokenizer=tokenizer,
      data_collator=self.data_collator,
      )
      print("Thank you for choosing Caribe \n")
      trainer.train()
      trainer.save_model("model/")
      
