import torch
from transformers import BertTokenizer, BertForSequenceClassification
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.model_selection import train_test_split
import pandas as pd
import json

# Load dataset from CSV file
data_df = pd.read_csv("../data/bird/tablenames_dataset.csv")

# Load schema information from JSON file
with open("../data/bird/processed_tables.json", "r") as file:
    schema_info = json.load(file)

# Binarize the table names (multi-label encoding)
mlb = MultiLabelBinarizer()
data_df['table_names_encoded'] = list(mlb.fit_transform(data_df['table_names'].apply(eval)))

# Split data into train and test
train_data, test_data = train_test_split(data_df, test_size=0.2, random_state=42)

# Custom Dataset class
class TablePredictionDataset(Dataset):
    def __init__(self, data, tokenizer, max_len, mlb):
        self.data = data
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.mlb = mlb

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

# Hyperparameters
MAX_LEN = 128
BATCH_SIZE = 8
EPOCHS = 3
LEARNING_RATE = 2e-5

# Tokenizer and Model
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertForSequenceClassification.from_pretrained(
    'bert-base-uncased',
    num_labels=len(mlb.classes_),
    problem_type="multi_label_classification"
)

# Datasets and DataLoaders
train_dataset = TablePredictionDataset(train_data, tokenizer, MAX_LEN, mlb)
test_dataset = TablePredictionDataset(test_data, tokenizer, MAX_LEN, mlb)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE)

# Optimizer and Loss Function
optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)
criterion = torch.nn.BCEWithLogitsLoss()

# Training Loop
def train_model(model, data_loader, optimizer, criterion, device):
    model.train()
    total_loss = 0

    for batch in data_loader:
        optimizer.zero_grad()

        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)

        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)

        loss = outputs.loss
        total_loss += loss.item()

        loss.backward()
        optimizer.step()

    return total_loss / len(data_loader)

# Evaluation Loop
def evaluate_model(model, data_loader, criterion, device):
    model.eval()
    total_loss = 0
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for batch in data_loader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)

            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)

            loss = outputs.loss
            total_loss += loss.item()

            preds = torch.sigmoid(outputs.logits).cpu()
            all_preds.append(preds)
            all_labels.append(labels.cpu())

    return total_loss / len(data_loader), torch.cat(all_preds), torch.cat(all_labels)

# Training the model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

for epoch in range(EPOCHS):
    train_loss = train_model(model, train_loader, optimizer, criterion, device)
    val_loss, preds, labels = evaluate_model(model, test_loader, criterion, device)

    print(f"Epoch {epoch + 1}/{EPOCHS}")
    print(f"Train Loss: {train_loss:.4f}")
    print(f"Validation Loss: {val_loss:.4f}")

# Save the model
model.save_pretrained("./multi_label_model")
tokenizer.save_pretrained("./multi_label_model")

print("Model training complete and saved!")
