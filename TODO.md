### TODO: Automate Message Updating

#### Step 1: Save Message and Channel Information
- [ ] Create a function to save message and channel IDs, along with team names.
  - [ ] Read existing data from a JSON file or a database.
  - [ ] Update the data with the new message and channel IDs.
  - [ ] Write the updated data back to the JSON file or database.

#### Step 2: Fetch and Update Message
- [ ] Create a function to update the message.
  - [ ] Read the saved message and channel IDs from the JSON file or database.
  - [ ] Use Discord.py's `fetch_message` and `get_channel` methods to retrieve the message and channel.
  - [ ] Update the message using the `edit` method.

#### Step 3: Command to Save Message Information
- [ ] Implement a command that calls the function from Step 1.
  - [ ] The command should save the IDs after sending a new message.

#### Step 4: Command to Update Message
- [ ] Implement a command that calls the function from Step 2.
  - [ ] The command should update the message without requiring any IDs as input.

#### Step 5: Test
- [ ] Test both commands to ensure they work as expected.
  - [ ] Test edge cases like missing IDs or invalid team names.

#### Step 6: Deployment
- [ ] Deploy the updated bot and test it in a live Discord server.
