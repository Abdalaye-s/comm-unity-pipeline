def generate_report(data, output_file):
    from fpdf import FPDF
    import matplotlib.pyplot as plt
    import os

    # Create a PDF class
    class PDF(FPDF):
        def header(self):
            self.set_font('Arial', 'B', 12)
            self.cell(0, 10, 'Sentiment Analysis Report', 0, 1, 'C')

        def footer(self):
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    # Create a PDF instance
    pdf = PDF()
    pdf.add_page()

    # Add a title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Analysis Results', 0, 1, 'C')

    # Add data to the PDF
    pdf.set_font('Arial', '', 12)
    for key, value in data.items():
        pdf.cell(0, 10, f'{key}: {value}', 0, 1)

    # Generate a graph
    plt.figure(figsize=(10, 6))
    plt.bar(data.keys(), data.values())
    plt.title('Sentiment Scores')
    plt.xlabel('Sentiment')
    plt.ylabel('Scores')
    graph_file = 'sentiment_graph.png'
    plt.savefig(graph_file)
    plt.close()

    # Add the graph to the PDF
    pdf.image(graph_file, x=10, y=pdf.get_y(), w=180)
    
    # Save the PDF
    pdf.output(output_file)

    # Clean up the graph file
    if os.path.exists(graph_file):
        os.remove(graph_file)