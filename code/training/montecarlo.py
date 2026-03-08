import io
import pickle
import chess
import chess.pgn
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt


# Helper function to convert a FEN string to a numerical array for the Neural Network
def fen_to_vector(fen):
    board = chess.Board(fen)
    vector = np.zeros(64, dtype=np.float32)
    # Basic piece values for numerical representation
    piece_values = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 10,
                    'p': -1, 'n': -3, 'b': -3, 'r': -5, 'q': -9, 'k': -10}
    
    for i in range(64):
        piece = board.piece_at(i)
        if piece:
            vector[i] = piece_values[piece.symbol()]
    return vector

def train_and_save_model(pickle_filename="montecarlo.pkl", save_path="montecarlo_model.keras", save_graph=False):
    """
    Reads FEN data from a Pickle file, trains a basic TensorFlow neural network, 
    plots the loss, and saves the model.
    """
    try:
        # 'rb' stands for 'read binary'
        with open(pickle_filename, 'rb') as file:
            mt_dict = pickle.load(file)
            print(f"Successfully loaded {len(mt_dict)} board states from {pickle_filename}")
    except FileNotFoundError:
        print(f"Error: Could not find the file '{pickle_filename}'. Make sure to create the pickle first.")
        return
    
    mt_dict = dict(list(mt_dict.items())[:100000])

    X = []
    y = []
    
    # Iterate directly over the dictionary structure
    for fen, (avg_score, count) in mt_dict.items():
        X.append(fen_to_vector(fen))
        y.append(avg_score)

    X = np.array(X)
    y = np.array(y)

    if len(X) == 0:
        print("No training data found. Aborting training.")
        return

    # Basic Neural Network architecture
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(64,)),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(1, activation='tanh') # Tanh outputs between -1 and 1
    ])

    model.compile(optimizer='adam', loss='mse', metrics=['mae'])
    
    print("Starting training process...")
    
    history = model.fit(X, y, epochs=15, batch_size=32, validation_split=0.2)
    
    model.save(save_path)
    print(f"Model saved successfully to {save_path}")

    # Plot the training and validation loss
    plt.figure(figsize=(10, 6))
    plt.plot(history.history['loss'], label='Training Loss (MSE)', linewidth=2)
    plt.plot(history.history['val_loss'], label='Validation Loss (MSE)', linewidth=2)
    plt.title('Model Loss over Epochs', fontsize=14)
    plt.xlabel('Epoch', fontsize=12)
    plt.ylabel('Loss (Mean Squared Error)', fontsize=12)
    plt.legend(fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    if save_graph:
        graph_filename = "training_loss_graph.png"
        plt.savefig(graph_filename)
        print(f"Training graph saved to {graph_filename}")
    plt.show()