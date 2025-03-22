import csv

def csv_to_html(csv_filename, html_filename):
    html_content = '''<div class="container">
    <div class="match">
        <span class="date">Date</span>
        <div class="teams">Home Team vs Away Team</div>
        <span class="winner">Winner</span>
    </div>\n'''
    with open(csv_filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            match_id, date, team1, team2 = row
            html_content += f'''
    <div class="match">
        <span class="date">{date}</span>
        <div class="teams">
            <span class="team home" onclick="setWinner(this)">{team1}</span> vs 
            <span class="team away" onclick="setWinner(this)">{team2}</span>
        </div>
        <div class="winner"></div>
    </div>
            '''
    
    html_content += '\n</div>'

    with open(html_filename, 'w', encoding='utf-8') as htmlfile:
        htmlfile.write(html_content)

    print(f"HTML file '{html_filename}' generated successfully!")

# Example usage
csv_to_html('ipl_2025_schedule.csv', 'game_html_format.html')
