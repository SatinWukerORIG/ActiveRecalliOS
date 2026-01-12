from openai import OpenAI

def main():
    client = OpenAI()

    response = client.responses.create(
        model="gpt-5-nano",
        input="Say 'API is working' in one short sentence."
    )

    print(response.output_text)

if __name__ == "__main__":
    main()
