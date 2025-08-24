package org.fax4j.server.http;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Entry point for the example HTTP fax server.
 */
@SpringBootApplication
public class HttpFaxServerApplication {
    public static void main(String[] args) {
        SpringApplication.run(HttpFaxServerApplication.class, args);
    }
}
