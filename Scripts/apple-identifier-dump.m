//
// This source file is part of the Grove FHIR open-source project
//
// SPDX-FileCopyrightText: 2026 Schmiedmayer Lab and the project authors (see CONTRIBUTORS.md)
//
// SPDX-License-Identifier: MIT
//
// Print the runtime value of each Apple identifier constant named on stdin.
//
// A producer tags an Observation with the value it reads back from the platform, not
// with the name of the constant that holds it. The two usually match; where they do
// not, only the value is a real source identifier. Sample types Apple exposes solely
// through a class accessor have no constant at all, so they are read from the type.

#import <Foundation/Foundation.h>
#import <HealthKit/HealthKit.h>
#import <SensorKit/SensorKit.h>
#import <dlfcn.h>

static void emit(NSString *name, NSString *value) {
    printf("%s\t%s\n", name.UTF8String, value.UTF8String);
}

int main(int argc, const char **argv) {
    @autoreleasepool {
        if (argc < 2) {
            fprintf(stderr, "usage: %s <file-of-constant-names>\n", argv[0]);
            return 2;
        }
        NSString *names = [NSString stringWithContentsOfFile:@(argv[1])
                                                    encoding:NSUTF8StringEncoding
                                                       error:nil];
        if (names == nil) {
            fprintf(stderr, "could not read %s\n", argv[1]);
            return 2;
        }
        int unresolved = 0;
        for (NSString *name in [names componentsSeparatedByString:@"\n"]) {
            if (name.length == 0) {
                continue;
            }
            void *symbol = dlsym(RTLD_DEFAULT, name.UTF8String);
            if (symbol == NULL) {
                fprintf(stderr, "unresolved: %s\n", name.UTF8String);
                unresolved += 1;
                continue;
            }
            emit(name, *(__unsafe_unretained NSString **)symbol);
        }
        emit(@"HKObjectType.electrocardiogramType()", HKObjectType.electrocardiogramType.identifier);
        emit(@"HKSampleType.audiogramSampleType()", HKSampleType.audiogramSampleType.identifier);
        return unresolved == 0 ? 0 : 1;
    }
}
