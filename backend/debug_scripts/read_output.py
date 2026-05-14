with open('output.txt', 'r', encoding='utf-16le') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if "Pipeline crashed for request" in line:
            start = max(0, i - 20)
            end = min(len(lines), i + 30)
            for j in range(start, end):
                print(lines[j].strip())
            break
