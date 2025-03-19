package com.jerrylearning;

import io.fabric8.kubernetes.api.model.Pod;
import io.fabric8.kubernetes.client.Config;
import io.fabric8.kubernetes.client.ConfigBuilder;
import io.fabric8.kubernetes.client.DefaultKubernetesClient;
import io.fabric8.kubernetes.client.KubernetesClient;
import javax.net.ssl.*;
import java.io.FileInputStream;
import java.io.InputStream;
import java.security.KeyStore;

import java.util.List;

/**
 * Hello world!
 *
 */
public class App 
{
    public static void configureSSL(String trustStorePath, String trustStorePassword) throws Exception {
        // Load the trust store
        KeyStore trustStore = KeyStore.getInstance("JKS");
        try (InputStream trustStoreInputStream = new FileInputStream(trustStorePath)) {
            trustStore.load(trustStoreInputStream, trustStorePassword.toCharArray());
        }

        // Create a TrustManager that trusts the certificates in the trust store
        TrustManagerFactory trustManagerFactory = TrustManagerFactory.getInstance(TrustManagerFactory.getDefaultAlgorithm());
        trustManagerFactory.init(trustStore);

        // Create an SSLContext and initialize it with the trust manager
        SSLContext sslContext = SSLContext.getInstance("TLS");
        sslContext.init(null, trustManagerFactory.getTrustManagers(), new java.security.SecureRandom());

        // Set the SSLContext as the default
        SSLContext.setDefault(sslContext);
    }


    public static void main( String[] args ) throws Exception {
        App.configureSSL("D:\\tools\\java8\\jre8\\lib\\security\\cacerts", "changeit");

        Config config = new ConfigBuilder()
                .withMasterUrl("https://47.119.56.113:6443/")
                .withOauthToken("eyJhbGciOiJSUzI1NiIsImtpZCI6IncxNVYweUtCbGlZWnRFUmdrbzJaNWEwWWNHVUU4OFhVNkY3aFdpTWpweFUifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6ImphdmEtYWNjZXNzLXNlY3JldCIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJqYXZhLWFkbWluIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiNWExZmUwMGQtMWZjZS00YjBjLTk1ZTYtNzI5OTdjNTkxNjg1Iiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50OmRlZmF1bHQ6amF2YS1hZG1pbiJ9.YvgqEmVKXhU0XHCR0RMGLn3sjbXONY9oj1TvXDuRSkGG3RJwJBJ3GxxfoxQBgFDydw-jlYHuosIzKPDxFeLbBulHnShKprk9w0821ehMvFAAhDoovSjEO1JaCKE6CJe_EO3egQR_xbyLCTxLgfdrkQQLRVbbw3M4RGq-3ONUhkwhq4nk_K8hqT3ZeInDmB9iM8tzhRNHFREmf5qrpKquVd162vOMv2KBhAYGMOAyoGOUX_Y1CoealTpo_zqd9BlzyG1-C3fx1YaP6OsPnl1Q3vRKbdipw1lxABKP8UGRJM9ZRH_bsuY32Kb8VNCdLAgEK-zD-NMr8jQhbMCUEqgR0w")
                .withCaCertFile("D:\\projects\\k8s_learn\\chapter_10_job\\k8s-fullchain.crt")
//            .withTrustCerts(true)
                .build();
        KubernetesClient client = new DefaultKubernetesClient(config);
        List<Pod> pods = client.pods().inNamespace("flask-ns").withLabel("app", "flask-app").list().getItems();
        System.out.println( "Number of pods = " + pods.size() );
        for (Pod pod : pods) {
            System.out.println("pod name = " + pod.getMetadata().getName());
        }
    }
}
