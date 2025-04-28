def create_graph(data, output_file):
    import matplotlib.pyplot as plt
    import seaborn as sns

    # Set the style of seaborn
    sns.set(style="whitegrid")

    # Create a bar plot
    plt.figure(figsize=(10, 6))
    sns.barplot(x=list(data.keys()), y=list(data.values()), palette="viridis")

    # Add titles and labels
    plt.title('Sentiment Analysis Results')
    plt.xlabel('Sentiment')
    plt.ylabel('Frequency')

    # Save the plot to a file
    plt.savefig(output_file)
    plt.close()