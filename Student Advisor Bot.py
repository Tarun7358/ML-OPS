import boto3
import time
from botocore.exceptions import ClientError

# ---------------------------
# Configuration
# ---------------------------
REGION = "us-east-1"     # Change if needed
BOT_ID = "YOUR_BOT_ID"   # Replace with your bot ID
BOT_VERSION = "DRAFT"
LOCALE_ID = "en_US"

# Initialize Lex V2 client
lex = boto3.client("lexv2-models", region_name=REGION)


# ---------------------------
# Step 1: Create Locale
# ---------------------------
def create_locale():
    try:
        lex.create_bot_locale(
            botId=BOT_ID,
            botVersion=BOT_VERSION,
            localeId=LOCALE_ID,
            nluIntentConfidenceThreshold=0.4
        )
        print(f"[+] Locale created: {LOCALE_ID}")
    except lex.exceptions.ConflictException:
        print(f"[*] Locale already exists: {LOCALE_ID}")


# ---------------------------
# Step 2: Create Slot Type
# ---------------------------
def create_slot_type():
    slot_type = lex.create_slot_type(
        slotTypeName="CourseNameType",
        description="Slot type for course names",
        slotTypeValues=[
            {"sampleValue": {"value": "Computer Science"}},
            {"sampleValue": {"value": "Physics"}},
            {"sampleValue": {"value": "Mathematics"}},
            {"sampleValue": {"value": "Chemistry"}},
            {"sampleValue": {"value": "Biology"}}
        ],
        valueSelectionSetting={"resolutionStrategy": "OriginalValue"},
        botId=BOT_ID,
        botVersion=BOT_VERSION,
        localeId=LOCALE_ID
    )
    print(f"[+] Slot type created: {slot_type['slotTypeId']}")


# ---------------------------
# Step 3: Create AskAboutAssignments Intent
# ---------------------------
def create_intent_assignments():
    lex.create_intent(
        intentName="AskAboutAssignments",
        sampleUtterances=[
            {"utterance": "When is the {CourseName} assignment due?"},
            {"utterance": "Tell me about the assignment for {CourseName}"},
            {"utterance": "What is the deadline for {CourseName} assignment?"}
        ],
        slots=[
            {
                "slotName": "CourseName",
                "slotTypeName": "CourseNameType",
                "valueElicitationSetting": {
                    "slotConstraint": "Required",
                    "promptSpecification": {
                        "maxRetries": 2,
                        "messageGroups": [
                            {
                                "message": {
                                    "plainTextMessage": {
                                        "value": "Which course assignment are you asking about?"
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        ],
        intentClosingSetting={
            "closingResponse": {
                "messageGroups": [
                    {
                        "message": {
                            "plainTextMessage": {
                                "value": "The assignment for {CourseName} is due next Friday at 5 PM."
                            }
                        }
                    }
                ]
            }
        },
        botId=BOT_ID,
        botVersion=BOT_VERSION,
        localeId=LOCALE_ID
    )
    print("[+] Intent created: AskAboutAssignments")


# ---------------------------
# Step 4: Create GetCourseInformation Intent
# ---------------------------
def create_intent_course_info():
    lex.create_intent(
        intentName="GetCourseInformation",
        sampleUtterances=[
            {"utterance": "Tell me about {CourseName}"},
            {"utterance": "Who teaches {CourseName}?"},
            {"utterance": "Give me details about {CourseName}"},
            {"utterance": "What is the schedule for {CourseName}?"}
        ],
        slots=[
            {
                "slotName": "CourseName",
                "slotTypeName": "CourseNameType",
                "valueElicitationSetting": {
                    "slotConstraint": "Required",
                    "promptSpecification": {
                        "maxRetries": 2,
                        "messageGroups": [
                            {
                                "message": {
                                    "plainTextMessage": {
                                        "value": "Which course do you want information about?"
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        ],
        intentClosingSetting={
            "closingResponse": {
                "messageGroups": [
                    {
                        "message": {
                            "plainTextMessage": {
                                "value": "The {CourseName} course is taught by Dr. Smith, "
                                         "has 3 credits, and meets on Mondays and Wednesdays at 10 AM."
                            }
                        }
                    }
                ]
            }
        },
        botId=BOT_ID,
        botVersion=BOT_VERSION,
        localeId=LOCALE_ID
    )
    print("[+] Intent created: GetCourseInformation")


# ---------------------------
# Step 5: Create Fallback Intent
# ---------------------------
def create_intent_fallback():
    lex.create_intent(
        intentName="FallbackIntent",
        intentClosingSetting={
            "closingResponse": {
                "messageGroups": [
                    {
                        "message": {
                            "plainTextMessage": {
                                "value": "Sorry, I didn’t understand that. Could you rephrase?"
                            }
                        }
                    }
                ]
            }
        },
        botId=BOT_ID,
        botVersion=BOT_VERSION,
        localeId=LOCALE_ID
    )
    print("[+] Intent created: FallbackIntent")


# ---------------------------
# Step 6: Build and Publish
# ---------------------------
def build_and_publish():
    print("[*] Building locale...")
    lex.build_bot_locale(
        botId=BOT_ID,
        botVersion=BOT_VERSION,
        localeId=LOCALE_ID
    )
    time.sleep(20)  # wait for build to process
    print("[+] Locale build started (check AWS Console for progress).")

    version = lex.create_bot_version(
        botId=BOT_ID,
        botVersionLocaleSpecification={"en_US": {"sourceBotVersion": "DRAFT"}}
    )
    print(f"[+] Bot published, version: {version['botVersion']}")

    alias = lex.create_bot_alias(
        botAliasName="Test",
        botId=BOT_ID,
        botVersion=version["botVersion"]
    )
    print(f"[+] Alias created: {alias['botAliasId']}")


# ---------------------------
# Main Execution
# ---------------------------
if __name__ == "__main__":
    try:
        create_locale()
        create_slot_type()
        create_intent_assignments()
        create_intent_course_info()
        create_intent_fallback()
        build_and_publish()
        print("[✓] Student Advisor Bot setup complete.")
    except ClientError as e:
        print("AWS Error:", e)
    except Exception as e:
        print("Unexpected Error:", e)
