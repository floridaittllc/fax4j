package org.fax4j.server.http;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import org.fax4j.FaxClient;
import org.fax4j.FaxClientFactory;
import org.fax4j.FaxJob;
import org.fax4j.FaxJobStatus;
import org.fax4j.bridge.http.HTTP2FaxBridge;
import org.fax4j.spi.http.HTTPRequest;
import org.fax4j.spi.http.HTTPRequest.ContentPart;
import org.fax4j.spi.http.HTTPRequest.ContentPartType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

/**
 * Simple controller exposing fax operations over HTTP.
 */
@RestController
@RequestMapping("/fax")
public class FaxController {
    private final HTTP2FaxBridge bridge;
    private final FaxClient faxClient;
    private final Map<String, FaxJob> jobs = new ConcurrentHashMap<>();

    public FaxController() {
        this.bridge = new HTTP2FaxBridge();
        this.bridge.initialize(null, null, this);
        // fax client for querying job status
        this.faxClient = FaxClientFactory.createFaxClient();
    }

    @PostMapping
    public Map<String, String> submitFax(@RequestPart("file") MultipartFile file,
            @RequestParam("targetaddress") String targetAddress,
            @RequestParam(value = "filename", required = false) String fileName,
            @RequestParam(value = "priority", required = false) String priority,
            @RequestParam(value = "targetname", required = false) String targetName,
            @RequestParam(value = "sendername", required = false) String senderName,
            @RequestParam(value = "senderfaxnumber", required = false) String senderFaxNumber,
            @RequestParam(value = "senderemail", required = false) String senderEmail) throws IOException {
        List<ContentPart<?>> parts = new ArrayList<>();
        parts.add(new ContentPart<>("file", file.getBytes(), ContentPartType.BINARY));
        String finalName = fileName != null ? fileName : file.getOriginalFilename();
        if (finalName != null) {
            parts.add(new ContentPart<>("filename", finalName, ContentPartType.STRING));
        }
        parts.add(new ContentPart<>("targetaddress", targetAddress, ContentPartType.STRING));
        if (priority != null) {
            parts.add(new ContentPart<>("priority", priority, ContentPartType.STRING));
        }
        if (targetName != null) {
            parts.add(new ContentPart<>("targetname", targetName, ContentPartType.STRING));
        }
        if (senderName != null) {
            parts.add(new ContentPart<>("sendername", senderName, ContentPartType.STRING));
        }
        if (senderFaxNumber != null) {
            parts.add(new ContentPart<>("senderfaxnumber", senderFaxNumber, ContentPartType.STRING));
        }
        if (senderEmail != null) {
            parts.add(new ContentPart<>("senderemail", senderEmail, ContentPartType.STRING));
        }

        HTTPRequest request = new HTTPRequest();
        request.setContent(parts.toArray(new ContentPart<?>[0]));

        FaxJob faxJob = this.bridge.submitFaxJob(request);
        String id = faxJob.getID();
        this.jobs.put(id, faxJob);

        Map<String, String> response = new HashMap<>();
        response.put("id", id);
        return response;
    }

    @GetMapping("/{id}")
    public ResponseEntity<Map<String, String>> getStatus(@PathVariable("id") String id) {
        FaxJob faxJob = this.jobs.get(id);
        if (faxJob == null) {
            return ResponseEntity.notFound().build();
        }
        FaxJobStatus status = this.faxClient.getFaxJobStatus(faxJob);
        Map<String, String> response = new HashMap<>();
        response.put("id", id);
        response.put("status", status.name());
        return ResponseEntity.ok(response);
    }
}
