### TODO: Automate Message Updating

#### Step 1: Save Message and Channel Information
- [X] Create a function to save message and channel IDs, along with team names.
  - [X] Read existing data from a JSON file or a database.
  - [X] Update the data with the new message and channel IDs.
  - [X] Write the updated data back to the JSON file or database.

#### Step 2: Fetch and Update Message
- [X] Create a function to update the message.
  - [X] Read the saved message and channel IDs from the JSON file or database.
  - [X] Use Discord.py's `fetch_message` and `get_channel` methods to retrieve the message and channel.
  - [X] Update the message using the `edit` method.

#### Step 3: Command to Update Message
- [X] Implement a command that calls the function from Step 2.
  - [X] The command should update the message without requiring any IDs as input.

#### Step 4: Test
- [X] Test both commands to ensure they work as expected.
  - [X] Test edge cases like missing IDs or invalid team names.

#### Step 5: Deployment
- [X] Deploy the updated bot and test it in a live Discord server.
