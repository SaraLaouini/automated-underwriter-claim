document.addEventListener('DOMContentLoaded', function () {
    const messageForm = document.getElementById('messageForm');
    const chatBox = document.getElementById('chatBox');

    let lastClaimID = 0;

    messageForm.addEventListener('submit', function (event) {
        event.preventDefault();
        const userMessageInput = document.getElementById('userMessage');
        const userMessage = userMessageInput.value.trim().toLowerCase(); 

        if (userMessage === '') return;

        appendMessage('user', userMessage);
        userMessageInput.value = '';

        
        setTimeout(() => {
            const systemResponse = simulateSystemResponse(userMessage);
            appendMessage('system', systemResponse);

            
            if (systemResponse.includes('Please provide details of the claim.')) {
                promptUserForClaimDetails();
            }
            
           
            chatBox.scrollTop = chatBox.scrollHeight;
        }, 500); 
    });

    function appendMessage(role, message) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message');
        messageElement.classList.add(role + '-message');
        messageElement.innerHTML = `<p>${message}</p>`;
        chatBox.appendChild(messageElement);

      
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function simulateSystemResponse(userMessage) {
    
    const insuranceKeywords = /(insurance|insure|insured|policy|claim|coverage|premium|underwriter|underwriting|deductible|exclusion|endorsement|adjuster|liability|coverage limit|coverage level|insurance company|insurer|reinsurance|reinsurer|risk|policyholder|loss|damage|accident|incident|beneficiary|indemnity)/i;

    if (insuranceKeywords.test(userMessage)) {
        return 'Please provide details of the claim.';
    } else {
        return "I'm sorry, I didn't understand that.";
    }
}


    function promptUserForClaimDetails() {
        
        lastClaimID++;

        const claimDetailsForm = document.createElement('form');
        claimDetailsForm.classList.add('claim-details-form');
        claimDetailsForm.innerHTML = `
            <input type="hidden" id="claimID" value="${lastClaimID}">
            <input type="text" id="policyNumber" placeholder="Policy Number" required>
            <input type="text" id="claimDate" placeholder="Claim Date" required>
            <input type="text" id="incidentDate" placeholder="Incident Date" required>
            <input type="text" id="reportedWithinPolicyTimeframe" placeholder="Reported Within Policy Timeframe" required>
            <input type="text" id="incidentType" placeholder="Incident Type" required>
            <input type="text" id="estimatedRepairCost" placeholder="Estimated Repair Cost" required>
            <input type="text" id="actualCashValue" placeholder="Actual Cash Value" required>
            <input type="text" id="claimAmount" placeholder="Claim Amount" required>
            <input type="text" id="policyCoverageLimit" placeholder="Policy Coverage Limit" required>
            <input type="text" id="deductible" placeholder="Deductible" required>
            <input type="text" id="driverAtFault" placeholder="Driver At Fault" required>
            <input type="text" id="legalActivityInvolved" placeholder="Legal Activity Involved" required>
            <input type="text" id="evidenceOfFraud" placeholder="Evidence Of Fraud" required>
            <input type="text" id="claimSeverity" placeholder="Claim Severity" required>
            <input type="text" id="totalLoss" placeholder="Total Loss" required>
            <input type="text" id="payableClaimAmount" placeholder="Payable Claim Amount" required>
            <input type="text" id="claimOutcome" placeholder="Claim Outcome" required>
            <input type="text" id="faultPercentage" placeholder="Fault Percentage" required>
            <input type="text" id="evidenceSources" placeholder="Evidence Sources" required>
            <input type="text" id="expertConsulted" placeholder="Expert Consulted" required>
            <input type="text" id="liabilityDisputed" placeholder="Liability Disputed" required>
            <button type="submit">Submit Claim Details</button>
        `;

        chatBox.appendChild(claimDetailsForm);

        claimDetailsForm.addEventListener('submit', function (event) {
            event.preventDefault();

            const claim = {
                ClaimID: document.getElementById('claimID').value.trim(),
                PolicyNumber: document.getElementById('policyNumber').value.trim(),
                ClaimDate: document.getElementById('claimDate').value.trim(),
                IncidentDate: document.getElementById('incidentDate').value.trim(),
                ReportedWithinPolicyTimeframe: document.getElementById('reportedWithinPolicyTimeframe').value.trim(),
                IncidentType: document.getElementById('incidentType').value.trim(),
                EstimatedRepairCost: document.getElementById('estimatedRepairCost').value.trim(),
                ActualCashValue: document.getElementById('actualCashValue').value.trim(),
                ClaimAmount: document.getElementById('claimAmount').value.trim(),
                PolicyCoverageLimit: document.getElementById('policyCoverageLimit').value.trim(),
                Deductible: document.getElementById('deductible').value.trim(),
                DriverAtFault: document.getElementById('driverAtFault').value.trim(),
                LegalActivityInvolved: document.getElementById('legalActivityInvolved').value.trim(),
                EvidenceOfFraud: document.getElementById('evidenceOfFraud').value.trim(),
                ClaimSeverity: document.getElementById('claimSeverity').value.trim(),
                TotalLoss: document.getElementById('totalLoss').value.trim(),
                PayableClaimAmount: document.getElementById('payableClaimAmount').value.trim(),
                ClaimOutcome: document.getElementById('claimOutcome').value.trim(),
                FaultPercentage: document.getElementById('faultPercentage').value.trim(),
                EvidenceSources: document.getElementById('evidenceSources').value.trim(),
                ExpertConsulted: document.getElementById('expertConsulted').value.trim(),
                LiabilityDisputed: document.getElementById('liabilityDisputed').value.trim(),
            };

            if (!claim.PolicyNumber || !claim.ClaimDate || !claim.IncidentDate || !claim.ReportedWithinPolicyTimeframe || !claim.IncidentType) {
                alert('Please fill in all required fields.');
                return;
            }

            submitClaimToLambda(claim);
        });
    }

    function submitClaimToLambda(claim) {
        appendMessage('system', 'Your claim details have been submitted successfully. Please wait while we generate a response.');

        fetch('https://4dbb4uhy5erfqbfaqhpcw52svq0nbqee.lambda-url.us-east-1.on.aws/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                doc_s3_path: 's3://buckett0/Auto Claim Acceptance Rules.pdf',
                Claim: claim,
            }),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            console.log('Lambda Response:', JSON.stringify(data, null, 2));

            if (data && data.claim_response && data.claim_response.body) {
                const claimResponseBody = JSON.parse(data.claim_response.body);
                if (claimResponseBody.prediction) {
                    appendMessage('system', `Prediction about your claim: ${claimResponseBody.prediction}`);
                } else {
                    appendMessage('system', 'Prediction data not available.');
                }
            } else {
                appendMessage('system', 'Prediction data not available.');
            }

            chatBox.scrollTop = chatBox.scrollHeight;
        })
        .catch((error) => {
            console.error('Error:', error);
            appendMessage('system', 'There was an error submitting your claim details. Please try again later.');

            chatBox.scrollTop = chatBox.scrollHeight;
        });
    }
});
