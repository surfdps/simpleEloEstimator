# How to install this crap

## Step 1: Clone the repo
```bash
git clone https://github.com/surfdps/simpleEloEstimator.git
```

## Step 2: Download stockfish 
Stockfish download is [here](https://stockfishchess.org/download/)

## Step 3: Edit main.py to include your username and stockfish path
```py
# SETTINGS
LICHESS_USERNAME = "YOUR_USERNAME"
STOCKFISH_PATH = "path_to_stockfish_executable" 
```

## Step 4: Edit the depth parameter
```py
DEPTH = 15
```
Usually 15 is enough, but you can use 30 to get deeper analysis, obviously it will be exponentially slower with each step

## Step 5: Launch this
```bash
python3 main.py
```

## Step 6: Be disappointed by your elo estimation
```plaintext

```