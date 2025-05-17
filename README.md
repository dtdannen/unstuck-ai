# unstuck-ai
MCP Server to ask humans for help

## Development Plan

Components:

1. MCP Server

    - [x] sends a kind 5109 event request for visual computer interaction help
    - [x] listens for feedback responses for prices and corresponding invoices
    - [ ] selects an offer by paying the invoice
    - [x] receives the result, returns it as the result of the MCP tool call
    - [ ] (testing) check invoice was paid in payment simulator before sending 6109
    - [ ] get image update working on digital ocean

2. Unstuck Frontend (Job Board and Workspace)
    - [ ] User login via Nostr
    - [ ] Pull job offers from Nostr relays
    - [ ] Allow user to set a default job amount in sats
    - [ ] Display job offers
    - [ ] Allow user to select a job
        - [ ] generate a lightning invoice for the amount
        - [ ] broadcast a kind 7000 event with the invoice and price
        - [ ] show a notification when the invoice was paid
    - [ ] Show a workspace like page for the user to do the work
    - [ ] Send the final job result event when the user is done

 
