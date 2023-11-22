# [IGDP-13] Adding software version as hard requirement for staging

Welcome to my MR. Some of the changes are listed below:

1. Added software version to staging model.
2. Added unit tests for valid software version, invalid software version, missing software version.

In addition to the changes above, there are also a few breaking changes introduced in this MR:

- Dropping all records which are missing software version.
   - **Affected downstream stakeholders**: Service, Analytics.
   - **Suggested remedy**: Handle deletions manualy, using the software version column in the exposures to identify source records
which will be dropped, and drop them in the target environment after our change is deployed.

For more information, please check out the Jira ticket associated with this MR, IGDP-13.