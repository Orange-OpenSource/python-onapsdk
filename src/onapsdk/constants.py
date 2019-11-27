#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Constant package."""

##
# State Machines
# Vendor: DRAFT --> CERTIFIED
# VSP: DRAFT --> UPLOADED --> VALIDATED --> COMMITED --> CERTIFIED
##

##
# States
##
DRAFT = "Draft"
CERTIFIED = "Certified"
COMMITED = "Commited"
UPLOADED = "Uploaded"
VALIDATED = "Validated"
APPROVED = "Approved"
UNDER_CERTIFICATION = "Certification in progress"
CHECKED_IN = "Checked In"
SUBMITTED = "Submitted"
DISTRIBUTED = "Distributed"
##
# Actions
##
CERTIFY = "Certify"
COMMIT = "Commit"
CREATE_PACKAGE = "Create_Package"
SUBMIT = "Submit"
SUBMIT_FOR_TESTING = "certificationRequest"
CHECKOUT = "checkout"
CHECKIN = "checkin"
APPROVE = "approve"
DISTRIBUTE = "PROD/activate"
TOSCA = "toscaModel"
DISTRIBUTION = "distribution"
START_CERTIFICATION = "startCertification"
NOT_CERTIFIED_CHECKOUT = "NOT_CERTIFIED_CHECKOUT"
NOT_CERTIFIED_CHECKIN = "NOT_CERTIFIED_CHECKIN"
READY_FOR_CERTIFICATION = "READY_FOR_CERTIFICATION"
CERTIFICATION_IN_PROGRESS = "CERTIFICATION_IN_PROGRESS"
DISTRIBUTION_APPROVED = "DISTRIBUTION_APPROVED"
DISTRIBUTION_NOT_APPROVED = "DISTRIBUTION_NOT_APPROVED"
SDC_DISTRIBUTED = "DISTRIBUTED"
##
# Distribution States
##
DOWNLOAD_OK = "DOWNLOAD_OK"
