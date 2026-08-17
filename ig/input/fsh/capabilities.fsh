//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//

// The server behaviour the Identifiers page states normatively, as a conformance
// resource rather than prose. Requirements-kind: it describes what a receiver must
// offer, not what any particular deployment does offer.

Instance: GroveDataReceiver
InstanceOf: CapabilityStatement
Usage: #definition
Title: "Grove Data Receiver"
Description: """
What a server has to offer to receive Grove uploads.

The load-bearing capability is conditional create on `identifier`: an uploader submits a
transaction Bundle whose entries carry `ifNoneExist: identifier={system}|{value}`, so a
record the platform re-reports — after a reinstall, a background retry, or a second
device syncing the same store — is recognised rather than duplicated. A server returns
`200` on a single existing match and `412` on multiple, which uploaders treat as a
data-hygiene signal rather than a transient failure. See the
[Identifiers](identifiers.html) page for the systems each platform uses.
"""
* name = "GroveDataReceiver"
* status = #draft
* experimental = false
* date = "2026-08-14"
* publisher = "Grove Alliance"
* kind = #requirements
* fhirVersion = #4.0.1
* format[0] = #json
* format[1] = #xml
* rest.mode = #server
* rest.documentation = "Receives mobile health uploads. Transport is TLS; authorization is a deployment concern this guide does not constrain."
* rest.interaction[0].code = #transaction
* rest.interaction[0].documentation = "Uploads arrive as transaction Bundles so a batch commits or fails whole."
* rest.resource[0].type = #Observation
* rest.resource[0].supportedProfile[0] = Canonical(GroveMobileSensorObservation)
* rest.resource[0].supportedProfile[1] = Canonical(GroveWearStateObservation)
* rest.resource[0].supportedProfile[2] = Canonical(GroveVisitObservation)
* rest.resource[0].supportedProfile[3] = Canonical(GroveDeviceUsageObservation)
* rest.resource[0].interaction[0].code = #create
* rest.resource[0].interaction[1].code = #search-type
* rest.resource[0].conditionalCreate = true
* rest.resource[0].conditionalDelete = #not-supported
* rest.resource[0].searchParam[0].name = "identifier"
* rest.resource[0].searchParam[0].type = #token
* rest.resource[0].searchParam[0].documentation = "The platform record identity; the discriminator conditional create keys on."
* rest.resource[0].searchParam[1].name = "patient"
* rest.resource[0].searchParam[1].type = #reference
* rest.resource[0].searchParam[2].name = "date"
* rest.resource[0].searchParam[2].type = #date
* rest.resource[0].searchParam[3].name = "code"
* rest.resource[0].searchParam[3].type = #token
* rest.resource[0].searchParam[4].name = "_source"
* rest.resource[0].searchParam[4].type = #uri
* rest.resource[0].searchParam[4].documentation = "The acquisition channel, denormalised onto `meta.source` because the contained Devices cannot be searched."
* rest.resource[0].searchParam[5].name = "_tag"
* rest.resource[0].searchParam[5].type = #token
* rest.resource[0].searchParam[5].documentation = "The recording device's form factor, denormalised onto `meta.tag` from the contained `Device.type`."
* rest.resource[1].type = #DocumentReference
* rest.resource[1].supportedProfile[0] = Canonical(GroveSensorBatchDocument)
* rest.resource[1].interaction[0].code = #create
* rest.resource[1].interaction[1].code = #search-type
* rest.resource[1].conditionalCreate = true
* rest.resource[1].searchParam[0].name = "identifier"
* rest.resource[1].searchParam[0].type = #token
* rest.resource[2].type = #QuestionnaireResponse
* rest.resource[2].supportedProfile[0] = Canonical(GroveQuestionnaireResponse)
* rest.resource[2].interaction[0].code = #create
* rest.resource[2].interaction[1].code = #search-type
* rest.resource[2].searchParam[0].name = "questionnaire"
* rest.resource[2].searchParam[0].type = #reference
* rest.resource[3].type = #Questionnaire
* rest.resource[3].supportedProfile[0] = Canonical(GroveQuestionnaire)
* rest.resource[3].interaction[0].code = #read
* rest.resource[3].interaction[1].code = #search-type
* rest.resource[3].searchParam[0].name = "url"
* rest.resource[3].searchParam[0].type = #uri
* rest.resource[3].searchParam[0].documentation = "Responses name their instrument by canonical URL, so a reader resolves it here."
