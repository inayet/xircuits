function checkInput(input: any, dataType: string): boolean {

    if(input === ""){
        alert("Input cannot be empty.");
        return false;
    }

    const normalizedDataType = dataType.toLowerCase();
    let processedInput = "";
    let errorDetails = "";
    let exampleInput = "";

    const formatError = (detail: string, example: string) => `Invalid ${dataType} input: ${detail} \nExample of a correct ${dataType} format: ${example}`;
    
    switch (normalizedDataType) {
        case "int":
        case "integer":
            // Regex: Matches possibly negative integers
            if(!/^\-?\d+$/.test(input)){
                errorDetails = "Input is not an integer.";
                exampleInput = "e.g. 3";
                alert(formatError(errorDetails, exampleInput));
                return false;
            }
            processedInput = `${input}`;
            break;
        case "float":
            // Regex: Matches possibly negative floats
            if(!/^\-?\d*\.\d+$/.test(input)){
                errorDetails = "Input is not a float.";
                exampleInput = "e.g. 3.14";
                alert(formatError(errorDetails, exampleInput));
                return false;
            }
            processedInput = `${input}`;
            break;
        case "string":
        case "secret":
        case "chat":
            processedInput = JSON.stringify(input);
            break;
        case "list":
        case "tuple": // validate tuple as list,as JS doesn't have native tuples
            processedInput = `[${input}]`;
            break;
        case "dict":
            processedInput = `{${input}}`;
            break;
        case "true":
        case "false":
        case "boolean":
            return true;
        case "undefined_any":
            //handler if called from any inputDialogue
            alert(`Type is undefined or not provided. Please insert the first character as shown in example.`);
            return false;
        default:
            alert("Invalid datatype: Please provide a valid datatype.");
            return false;
    }

    try {
        JSON.parse(processedInput);
    } catch (e) {
        if (processedInput.includes("'")) {
            errorDetails = "Please use double quotes instead of single quotes.";
        } else if (/(?:\{|\[|\()(?:\w+)/.test(processedInput)) {
            errorDetails = "Please ensure to use double quotes for your variables.";
        } else {
            errorDetails = "Please check the console log for details.";
            console.error("Parsing error:", e.message);
        }

        switch (normalizedDataType) {
            case "string":
            case "secret":
                exampleInput = '"example_string"';
                break;
            case "tuple":
            case "list":
                exampleInput = '"item1", "item2", 123';
                break;
            case "dict":
                exampleInput = '"key1": "value1", "key2": 123';
                break;
        }

        if (normalizedDataType !== "secret") {
            errorDetails += "\n\nYour input: " + input;
        }

        alert(formatError(errorDetails, exampleInput));
        return false;
    }

    return true;
}

export { checkInput };
