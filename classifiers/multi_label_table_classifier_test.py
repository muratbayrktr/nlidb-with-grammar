import torch
from transformers import BertTokenizer, BertForSequenceClassification
from torch.utils.data import DataLoader, Dataset
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.preprocessing import MultiLabelBinarizer
import pandas as pd
import json

model_dir = "./multi_label_model"  
tokenizer = BertTokenizer.from_pretrained(model_dir)
model = BertForSequenceClassification.from_pretrained(model_dir)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

test_data = pd.read_csv("../data/bird/tablenames_dataset.csv") 
with open("../data/bird/processed_tables.json", "r") as file:
    schema_info = json.load(file)

mlb = MultiLabelBinarizer()
mlb.fit([eval(x) for x in test_data['table_names']])  

test_data['table_names_encoded'] = list(mlb.transform(test_data['table_names'].apply(eval)))

class TablePredictionDataset(Dataset):
    def __init__(self, data, tokenizer, max_len):
        self.data = data
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        question = self.data.iloc[idx]['question']
        db_id = self.data.iloc[idx]['db_id']
        input_text = f"{question} [SEP] {db_id}"
        labels = torch.tensor(self.data.iloc[idx]['table_names_encoded'], dtype=torch.float)

        inputs = self.tokenizer(
            input_text,
            padding='max_length',
            truncation=True,
            max_length=self.max_len,
            return_tensors="pt"
        )

        return {
            'input_ids': inputs['input_ids'].squeeze(0),
            'attention_mask': inputs['attention_mask'].squeeze(0),
            'labels': labels
        }

MAX_LEN = 128
BATCH_SIZE = 8
test_dataset = TablePredictionDataset(test_data, tokenizer, MAX_LEN)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE)

def evaluate_model(model, data_loader, device):
    model.eval()
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for batch in data_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            preds = torch.sigmoid(logits).cpu()

            print("Raw logits:", logits[:5])  
            print("Probabilities:", preds[:5]) 
            print("Labels:", labels[:5].cpu())  

            all_preds.append(preds)
            all_labels.append(labels.cpu())

    all_preds = torch.cat(all_preds).numpy()
    all_labels = torch.cat(all_labels).numpy()

    threshold = 0.5
    all_preds = (all_preds >= threshold).astype(int)
    print("Predictions after thresholding:", all_preds[:5])

    accuracy = accuracy_score(all_labels, all_preds)
    precision, recall, f1, _ = precision_recall_fscore_support(all_labels, all_preds, average='micro')

    return accuracy, precision, recall, f1

accuracy, precision, recall, f1 = evaluate_model(model, test_loader, device)

print(f"Accuracy: {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall: {recall:.4f}")
print(f"F1 Score: {f1:.4f}")
