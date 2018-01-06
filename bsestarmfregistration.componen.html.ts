<!--mat-toolbar color="primary" -->
<div fxLayout="row" fxLayoutWrap fxLayout.lt-sm="column" class="natheader natheadertitle"  fxLayoutGap="20px" fxLayoutAlign="center center" >
<span fxFlex>Register your details</span>
<div >
<button mat-raised-button fxFlexAlign.lt-sm="start" color="accent"><strong>Save for Later</strong></button>
<button  mat-raised-button fxFlexAlign.lt-sm="end" color="accent" style="color:white" [disabled]="!(clientdetails.valid && clientaddress.valid && clientbank.valid && clientfatca.valid)"><strong>Submit</strong></button>
</div>
</div>
<!--/mat-toolbar-->
<mat-card>
<mat-horizontal-stepper [linear]="isLinear">
    <mat-step [stepControl]="clientdetails">
      <form [formGroup]="clientdetails" >
        <ng-template matStepLabel>Your Details</ng-template>
        
        <mat-card>
        <div fxLayout="column"  fxLayoutGap="50px"  >
         
          <div fxLayout="row" fxLayout.lt-md="column" fxLayoutGap="30px" fxLayoutAlign="center center">
              <mat-form-field class="example-full-width" fxFlex="60%" >
                  <input matInput placeholder="Name"  formControlName="clientname"  [(ngModel)]="regdet.clientname" readonly>
                </mat-form-field>
                <span fxFlex></span>
                <!--
                <mat-form-field class="example-full-width" fxFlex fxHide="true" >
                    <input matInput placeholder="ClientCode" formControlName="clientcode" [(ngModel)]="regdet.clientcode">
                  </mat-form-field>
                  -->
                <mat-form-field class="example-full-width" fxFlex >
                    <input matInput placeholder="PAN" formControlName="clientpan" [(ngModel)]="regdet.clientpan" readonly>
                  </mat-form-field>
                
          
          </div>
          <div fxLayout="row" fxLayout.lt-md="column" fxLayoutGap="30px" fxLayoutAlign="center center">
              <mat-form-field class="example-full-width" fxFlex >
                  <input matInput placeholder="email"  formControlName="clientemail" [(ngModel)]="regdet.clientemail" readonly>
                </mat-form-field>
                <mat-form-field class="example-full-width" fxFlex >
                    <input matInput placeholder="Mobile"  formControlName="clientmobile" [(ngModel)]="regdet.clientmobile" readonly>
                  </mat-form-field>

                  <!--Client communication mode default to E- Electronic
                  <mat-form-field class="example-full-width" fxFlex >
                      <mat-select placeholder="Comunication Mode" formControlName="clientcommode" [(ngModel)]="regdet.clientcommode">
                        <mat-option *ngFor="let food of foods" [value]="food.value">
                          {{ food.viewValue }}
                        </mat-option>
                      </mat-select>
                    </mat-form-field>
                    -->
          </div>


          <div fxLayout="row" fxLayout.lt-md="column" fxLayoutGap="30px" fxLayoutAlign="center center">


              <mat-radio-group class="example-full-width"  fxFlex fxAlign="end" formControlName="clientgender" [(ngModel)]="regdet.clientgender">
                  <mat-radio-button value="1"  >Male</mat-radio-button>
                  <mat-radio-button value="2" >Female</mat-radio-button>                  
                </mat-radio-group>

              

                <mat-form-field fxFlex class="example-full-width" >
                    <input matInput [matDatepicker]="picker" placeholder="DOB" formControlName="clientdob" [(ngModel)]="regdet.clientdob">
                    <mat-datepicker-toggle matSuffix [for]="picker"></mat-datepicker-toggle>
                    <mat-datepicker #picker></mat-datepicker>
                  </mat-form-field>
                  
                  <mat-form-field fxFlex class="example-full-width">
                    <mat-select placeholder="Client Occupation Code" formControlName="clientocupation" [(ngModel)]="regdet.clientocupation">
                      <mat-option *ngFor="let occupationcode of occupationcodes" [value]="occupationcode.code">
                        {{ occupationcode.valuestr }}
                      </mat-option>
                    </mat-select>
                  </mat-form-field>

                <!--span fxFlex fxHide.lt-md></span>
              <span fxFlex fxHide.lt-md></span>
                  <mat-form-field class="example-full-width" fxFlex fxHide="true" class="example-full-width" >
                      <input matInput placeholder="HOLDING" formControlName="clientholding" [(ngModel)]="regdet.clientholding">
                    </mat-form-field-->


          </div>

          <div fxLayout="row" fxLayout.lt-md="column" fxLayoutGap="30px"  fxLayoutAlign="center center"> 
              <mat-checkbox fxFlex class="example-full-width" formControlName="clientpepflg" [(ngModel)]="regdet.clientpepflg">politically exposed person (PEP)</mat-checkbox>
          </div>

          <div fxLayout="row" fxLayout.lt-md="column" fxLayoutGap="30px"  fxLayoutAlign="center center"> 

              <mat-checkbox fxFlex class="example-full-width" formControlName="clientisnri" [(ngModel)]="regdet.clientisnri" (change)="tooglenri($event)">NRI</mat-checkbox>

              <mat-radio-group fxFlex class="example-full-width" formControlName="clienttaxstatusres" [(ngModel)]="regdet.clienttaxstatusres" *ngIf="!nristatus">
                  <mat-radio-button [checked]="!nristatus">Resident Individual</mat-radio-button>

                </mat-radio-group>

              <mat-radio-group fxFlex class="example-full-width" formControlName="clienttaxstatusnri" [(ngModel)]="regdet.clienttaxstatusnri" *ngIf="nristatus">
                <mat-radio-button value="NRE"> NRE</mat-radio-button>
                <mat-radio-button value="NRO">NRO</mat-radio-button>
              </mat-radio-group>
              <!--Looks like these are place and country of incorporation shld not be for individuals  
              <mat-form-field fxFlex class="example-full-width" *ngIf="nristatus">
                  <mat-select placeholder="Place of Birth" formControlName="clientpobirth" [(ngModel)]="regdet.clientpobirth">
                    <mat-option *ngFor="let food of foods" [value]="food.value">
                      {{ food.viewValue }}
                    </mat-option>
                  </mat-select>
                </mat-form-field>
                <mat-form-field fxFlex class="example-full-width" *ngIf="nristatus">
                    <mat-select placeholder="Country of Birth" formControlName="clientcoubirth" [(ngModel)]="regdet.clientcoubirth">
                      <mat-option *ngFor="let food of foods" [value]="food.value">
                        {{ food.viewValue }}
                      </mat-option>
                    </mat-select>
                  </mat-form-field>
                -->

          </div>

          <div fxLayout="row" fxLayout.lt-md="column" fxLayoutGap="30px"  fxLayoutAlign="center center"> 
              <mat-checkbox fxFlex class="example-full-width"  formControlName="clienthasnominee" [(ngModel)]="regdet.clienthasnominee" (change)="tooglenominee($event)">Want to add nominee to my investments</mat-checkbox>

          </div>

         
        <div fxLayout="row" fxLayout.lt-md="column" fxLayoutGap="30px"  fxLayoutAlign="center center" *ngIf="hasnominee"> 

        <mat-form-field class="example-full-width" fxFlex>
            <input matInput placeholder="NomineeName"  formControlName="clientnomineename" [(ngModel)]="regdet.clientnomineename" >
          </mat-form-field>

          <mat-form-field fxFlex class="example-full-width" >
            <mat-select placeholder="Relation" formControlName="clientnomineerel" [(ngModel)]="regdet.clientnomineerel" >
              <mat-option *ngFor="let nominrel of nominrels" [value]="nominrel">
                {{ nominrel }}
              </mat-option>
            </mat-select>
          </mat-form-field>



            <mat-form-field fxFlex class="example-full-width" >
                <input matInput [matDatepicker]="picker1" placeholder="Nominee DOB" formControlName="clientnomineedob" [(ngModel)]="regdet.clientnomineedob">
                <mat-datepicker-toggle matSuffix [for]="picker"></mat-datepicker-toggle>
                <mat-datepicker #picker></mat-datepicker>
              </mat-form-field>

              <mat-form-field class="example-full-width" fxFlex>
                  <textarea matInput placeholder="Nominee Address" formControlName="clientnomineeaddres" [(ngModel)]="regdet.clientnomineeaddres"></textarea>
                </mat-form-field>


        </div>



            </div>
        </mat-card>
        <br>
        <br>
        <div >

            <span fxFlex></span>
            <button mat-raised-button color="primary" matStepperNext (click)="myfunc()" [disabled]="!(clientdetails.valid)">Next</button>
            
        </div>
        <div>
            <span fxFlex></span>
            <p style="color:green">*Auto saved on navigating to next page</p>
          
        </div>
            <div> <!-- HiddenFile -->

              <!-- HiddenFile for holding type always Physical-->
              <mat-form-field class="example-full-width" fxFlex fxHide="true" class="example-full-width" >
                  <input matInput placeholder="HOLDING" formControlName="clientfndhldtype" [(ngModel)]="regdet.clientfndhldtype">
                  
                </mat-form-field>

              
            </div>


      </form>

  
    </mat-step>

    <mat-step [stepControl]="clientaddress">
        <form [formGroup]="clientaddress" >
          <ng-template matStepLabel>Address Details</ng-template>
          <mat-card>
          <div fxLayout="column" fxLayoutGap="50px" >
           <h3>Residence Address</h3>
              <div fxLayout="row" fxLayout.lt-md="column" fxLayoutGap="30px"  fxLayoutAlign="center center">
                  <mat-form-field class="example-full-width" fxFlex  >
                      <input matInput placeholder="Resident Adress1" formControlName="clientaddress1" [(ngModel)]="regdet.clientaddress1">
                      <mat-error *ngIf="clientaddress.controls['clientaddress1'].hasError('maxlength')">Max Lenght 40</mat-error>
                      <mat-error *ngIf="clientaddress.controls['clientaddress1'].hasError('required')">Address1 is required</mat-error>
                    </mat-form-field>
                    <mat-form-field class="example-full-width" fxFlex  >
                        <input matInput placeholder="Resident Adress2" formControlName="clientaddress2" [(ngModel)]="regdet.clientaddress2">
                        <mat-error *ngIf="clientaddress.controls['clientaddress2'].hasError('maxlength')">Max Lenght 40</mat-error>
                      </mat-form-field>
                      <mat-form-field class="example-full-width" fxFlex  >
                          <input matInput placeholder="Resident Adress3" formControlName="clientaddress3" [(ngModel)]="regdet.clientaddress3">
                          <mat-error *ngIf="clientaddress.controls['clientaddress3'].hasError('maxlength')">Max Lenght 40</mat-error>
                        </mat-form-field>

            </div>
            <div fxLayout="row" fxLayout.lt-md="column" fxLayoutGap="30px"  fxLayoutAlign="center center">
                <mat-form-field class="example-full-width" fxFlex  >
                    <input matInput placeholder="City" formControlName="clientcity" [(ngModel)]="regdet.clientcity">
                  </mat-form-field>

   
                  <mat-form-field fxFlex class="example-full-width" >
                      <mat-select placeholder="State" formControlName="clientstate" [(ngModel)]="regdet.clientstate">
                        <mat-option *ngFor="let state of states" [value]="state">
                          {{ state }}
                        </mat-option>
                      </mat-select>
                    </mat-form-field>

                <mat-form-field class="example-full-width" fxFlex  >
                          <input matInput placeholder="Country" formControlName="clientcountry" [(ngModel)]="regdet.clientcountry">
                </mat-form-field>
              <mat-form-field class="example-full-width" fxFlex  >
                    <input matInput placeholder="PinCode" formControlName="clientpincode">
                  </mat-form-field>

          </div>


            <h3 *ngIf="nristatus">Foreign Address</h3>
            <div fxLayout="row" fxLayout.lt-md="column" fxLayoutGap="30px"  fxLayoutAlign="center center" *ngIf="nristatus">
                <mat-form-field class="example-full-width" fxFlex  >
                    <input matInput placeholder="Foreign Adress1" formControlName="clientforinadd1" [(ngModel)]="regdet.clientforinadd1">
                    <mat-error *ngIf="clientaddress.controls['clientforinadd1'].hasError('maxlength')">Max Lenght 40</mat-error>
                    <mat-error *ngIf="clientaddress.controls['clientforinadd1'].hasError('required')">Address1 is required</mat-error>
                  </mat-form-field>
                  <mat-form-field class="example-full-width" fxFlex  >
                      <input matInput placeholder="Foreign Adress1" formControlName="clientforinadd2" [(ngModel)]="regdet.clientforinadd2">
                      <mat-error *ngIf="clientaddress.controls['clientforinadd2'].hasError('maxlength')">Max Lenght 40</mat-error>
                    </mat-form-field>
                    <mat-form-field class="example-full-width" fxFlex  >
                        <input matInput placeholder="Foreign Adress3" formControlName="clientforinadd3" [(ngModel)]="regdet.clientforinadd3">
                        <mat-error *ngIf="clientaddress.controls['clientforinadd3'].hasError('maxlength')">Max Lenght 40</mat-error>
                      </mat-form-field>

          </div>
          <div fxLayout="row" fxLayout.lt-md="column" fxLayoutGap="30px"  fxLayoutAlign="center center" *ngIf="nristatus">
              <mat-form-field class="example-full-width" fxFlex  >
                  <input matInput placeholder="City" formControlName="clientforcity" [(ngModel)]="regdet.clientforcity">
                </mat-form-field>

                  <mat-form-field class="example-full-width" fxFlex  >
                    <input matInput placeholder="State" formControlName="clientforstate" [(ngModel)]="regdet.clientforstate">
                  </mat-form-field>

                  <mat-form-field fxFlex class="example-full-width" >
                      <mat-select placeholder="Country" formControlName="clientforcountry" [(ngModel)]="regdet.clientforcountry">
                        <mat-option *ngFor="let country of countrys" [value]="country">
                          {{ country }}
                        </mat-option>
                      </mat-select>
                    </mat-form-field>

            <mat-form-field class="example-full-width" fxFlex  >
                  <input matInput placeholder="PinCode" formControlName="clientforpin" [(ngModel)]="regdet.clientforpin">
                </mat-form-field>

        </div>     

          </div>
          
        </mat-card>
          <br>
          <br>
          <div fxLayoutGap="30px">
              <span fxFlex></span>
              <button mat-raised-button color="primary" matStepperPrevious >Back</button>
              <button mat-raised-button color="primary" matStepperNext >Next</button>
              
            </div>
        </form>
    </mat-step>

    <mat-step [stepControl]="clientbank">
        <form [formGroup]="clientbank" >
          <ng-template matStepLabel>Bank Details</ng-template>
          <mat-card>
          <div fxLayout="column" fxLayoutGap="50px" >
           
          <div fxLayout="row" fxLayout.lt-md="column" fxLayoutGap="30px" fxLayoutAlign="start center">
              <mat-form-field class="example-full-width" fxFlex.gt-sm="300px" fxAlign="start">
                <input matInput placeholder="Bank IFSC" name="bankifsc" formControlName="clientifsc" [(ngModel)]="regdet.clientifsc" (onchange)="getbankdata($event)">
              </mat-form-field>
              <label for="bankifsc" fxFlex *ngIf="ifscdet.failed" style="color:red">{{ifscdet.errormsg}}</label>
              <label for="bankifsc" fxFlex *ngIf="!ifscdet.failed" style="color:green">
                <h3>{{ifscdet.bank}}&nbsp;&nbsp;</h3>{{ifscdet.branch}}&nbsp;{{ifscdet.address}}&nbsp;{{ifscdet.city}}&nbsp;{{ifscdet.state}}
              </label>

            </div>
						 <div> <!-- HiddenFile -->

              <!-- HiddenFile for holding type always Physical-->
              <mat-form-field class="example-full-width" fxFlex fxHide="true" class="example-full-width" >
                  <input matInput placeholder="HOLDING" formControlName="clientmicrno" [(ngModel)]="regdet.clientmicrno">
                  
                </mat-form-field>

              
            </div>
            <div fxLayout="row" fxLayout.lt-md="column" fxLayoutGap="30px"  fxLayoutAlign="center center">
                <mat-form-field class="example-full-width" fxFlex>
                    <input matInput placeholder="Account Number" formControlName="clientacnumb" [(ngModel)]="regdet.clientacnumb">
                  </mat-form-field>

                  <mat-radio-group class="example-full-width"  fxFlex formControlName="clientactype" [(ngModel)]="regdet.clientactype" fxAlign="end">
                      <mat-radio-button value="SB" >Savings</mat-radio-button>
                      <mat-radio-button value="CB" >Current</mat-radio-button>
                      <mat-radio-button value="NE" >NRE</mat-radio-button>
                      <mat-radio-button value="NO" >NRO</mat-radio-button>
                    </mat-radio-group>
            </div>
			



          </div>
        </mat-card>
        <br>
        <br>
        <div fxLayoutGap="30px">
            <span fxFlex></span>
            <button mat-raised-button color="primary" matStepperPrevious >Back</button>
            <button mat-raised-button color="primary" matStepperNext >Next</button>
            
          </div>
        </form>
    </mat-step>

    <mat-step [stepControl]="clientfatca">
        <form [formGroup]="clientfatca" >
          <ng-template matStepLabel>Tax Details</ng-template>
          <mat-card>
          <div fxLayout="column" fxLayoutGap="50px" >
           
              <div fxLayout="row" fxLayout.lt-md="column" fxLayoutGap="30px" fxLayoutAlign="start center">
                  <h3> Tax Country 1 : &nbsp;</h3>
                  <mat-form-field fxFlex class="example-full-width" >
                      <mat-select placeholder="Country" formControlName="clienttaxrescntry1" [(ngModel)]="regdet.clienttaxrescntry1">
                        <mat-option *ngFor="let country of fcountrys" [value]="country">
                          {{ country }}
                        </mat-option>
                      </mat-select>
                    </mat-form-field>
                    <mat-form-field fxFlex class="example-full-width" >
                      <mat-select placeholder="ID Type" formControlName="clienttaxidtype1" [(ngModel)]="regdet.clienttaxidtype1">
                        <mat-option *ngFor="let fidtype of fidtypes" [value]="fidtype.code">
                          {{ fidtype.valuestr }}
                        </mat-option>
                      </mat-select>
                    </mat-form-field>
                    <mat-form-field class="example-full-width" fxFlex>
                      <input matInput placeholder="Tax ID" formControlName="clienttaxid1" [(ngModel)]="regdet.clienttaxid1">
                    </mat-form-field>                    
            </div>

            <div fxLayout="row" fxLayout.lt-md="column" fxLayoutGap="30px" fxLayoutAlign="start center">
            <h3> Tax Country 2 : &nbsp;</h3>
            <mat-form-field fxFlex class="example-full-width" >
                <mat-select placeholder="Country" formControlName="clienttaxrescntry2" [(ngModel)]="regdet.clienttaxrescntry2">
                  <mat-option *ngFor="let country of fcountrys" [value]="country">
                    {{ country }}
                  </mat-option>
                </mat-select>
              </mat-form-field>
              <mat-form-field fxFlex class="example-full-width" >
                <mat-select placeholder="ID Type" formControlName="clienttaxidtype2" [(ngModel)]="regdet.clienttaxidtype2">
                  <mat-option *ngFor="let fidtype of fidtypes" [value]="fidtype.code">
                    {{ fidtype.valuestr }}
                  </mat-option>
                </mat-select>
              </mat-form-field>
              <mat-form-field class="example-full-width" fxFlex>
                <input matInput placeholder="Tax ID" formControlName="clienttaxid2" [(ngModel)]="regdet.clienttaxid2">
              </mat-form-field>                    
        </div>
            

        <div fxLayout="row" fxLayout.lt-md="column" fxLayoutGap="30px" fxLayoutAlign="start center">
          <h3> Tax Country 3 : &nbsp;</h3>
          <mat-form-field fxFlex class="example-full-width" >
              <mat-select placeholder="Country" formControlName="clienttaxrescntry3" [(ngModel)]="regdet.clienttaxrescntry3">
                <mat-option *ngFor="let country of fcountrys" [value]="country">
                  {{ country }}
                </mat-option>
              </mat-select>
            </mat-form-field>
            <mat-form-field fxFlex class="example-full-width" >
              <mat-select placeholder="ID Type" formControlName="clienttaxidtype3" [(ngModel)]="regdet.clienttaxidtype3">
                <mat-option *ngFor="let fidtype of fidtypes" [value]="fidtype.code">
                  {{ fidtype.valuestr }}
                </mat-option>
              </mat-select>
            </mat-form-field>
            <mat-form-field class="example-full-width" fxFlex>
              <input matInput placeholder="Tax ID" formControlName="clienttaxid3" [(ngModel)]="regdet.clienttaxid3">
            </mat-form-field>                    
      </div>
          

      <div fxLayout="row" fxLayout.lt-md="column" fxLayoutGap="30px" fxLayoutAlign="start center">
        <h3> Tax Country 4 : &nbsp;</h3>
        <mat-form-field fxFlex class="example-full-width" >
            <mat-select placeholder="Country" formControlName="clienttaxrescntry4" [(ngModel)]="regdet.clienttaxrescntry4">
              <mat-option *ngFor="let country of fcountrys" [value]="country">
                {{ country }}
              </mat-option>
            </mat-select>
          </mat-form-field>
          <mat-form-field fxFlex class="example-full-width" >
            <mat-select placeholder="ID Type" formControlName="clienttaxidtype4" [(ngModel)]="regdet.clienttaxidtype4">
              <mat-option *ngFor="let fidtype of fidtypes" [value]="fidtype.code">
                {{ fidtype.valuestr }}
              </mat-option>
            </mat-select>
          </mat-form-field>
          <mat-form-field class="example-full-width" fxFlex>
            <input matInput placeholder="Tax ID" formControlName="clienttaxid4" [(ngModel)]="regdet.clienttaxid4">
          </mat-form-field>                    
    </div>
    <div fxLayout="row" fxLayout.lt-md="column" fxLayoutGap="30px" fxLayoutAlign="start center">
        
          <mat-form-field class="example-full-width" fxFlex>
            <input matInput placeholder="Place Of Birth" formControlName="clientpobir" [(ngModel)]="regdet.clientpobir">
          </mat-form-field>      
          <mat-form-field fxFlex class="example-full-width" >
              <mat-select placeholder="Country Of Birth" formControlName="clientcobir" [(ngModel)]="regdet.clientcobir">
                <mat-option *ngFor="let country of fcountrys" [value]="country">
                  {{ country }}
                </mat-option>
              </mat-select>
            </mat-form-field>
            <span fxFlex></span>
            <span fxFlex></span>            
    </div>




          </div>
        </mat-card>
        <br>
        <br>
        <div fxLayoutGap="30px">
            <span fxFlex></span>
            <button mat-raised-button color="primary" matStepperPrevious >Back</button>
            <button mat-raised-button color="primary" matStepperNext >Next</button>
           
          </div>
        </form>
    </mat-step>

    <mat-step >
        <form  >
          <ng-template matStepLabel>Document upload</ng-template>
          <mat-card>
          <div fxLayout="column" fxLayoutGap="50px" >
           
            <div fxLayout="row" fxLayoutGap="30px" >
              <div fxFlex>
            <h4 >Upload your AOF</h4>
          </div>
          <div fxFlex ="30%">
            <button mat-mini-fab color="accent" (click)="fileInput.click()">
              <mat-icon>attach_file</mat-icon> 
                <input #fileInput type="file" (change)="onFileInput($event)" style="display:none;" />
            </button>        
            <mat-form-field>
              <input matInput type="text" [value]="fileName" disabled>
              <mat-hint *ngIf="filevalerror">{{filvaldiationmsg}}</mat-hint>
            </mat-form-field>
            </div>
            <span fxFlex></span>
            <div fxFlex>  
            <button mat-raised-button color="accent" (click)="uploadFile()">
                <mat-icon>file_upload</mat-icon> 
                UploadFile                  
              </button>
            </div>
              <!--http://www.advancesharp.com/blog/1218/angular-4-upload-files-with-data-and-web-api-by-drag-drop
              https://www.youtube.com/watch?v=FI7bzIuPous     -->                          
            </div>


            <hr>

            <div fxLayout="row" fxLayoutGap="30px" >
                <div fxFlex>
              <h4 >Cancelled Cheque</h4>
            </div>
            <div fxFlex ="30%">
              <button mat-mini-fab color="accent" (click)="fileInput.click()">
                <mat-icon>attach_file</mat-icon> 
                  <input #fileInput type="file" (change)="onFileInput($event)" style="display:none;" />
              </button>        
              <mat-form-field>
                <input matInput type="text" [value]="fileName" disabled>
                <mat-hint *ngIf="filevalerror">{{filvaldiationmsg}}</mat-hint>
              </mat-form-field>
              </div>
              <span fxFlex></span>
              <div fxFlex>  
              <button mat-raised-button color="accent" (click)="uploadFile()">
                  <mat-icon>file_upload</mat-icon> 
                  UploadFile                  
                </button>
              </div>
                <!--http://www.advancesharp.com/blog/1218/angular-4-upload-files-with-data-and-web-api-by-drag-drop
                https://www.youtube.com/watch?v=FI7bzIuPous     -->                          
              </div>

              <hr>


          </div>
          <br>
          <br>
          <br>
        </mat-card>
        <br>
        <br>
        <div fxLayoutGap="30px">
            <span fxFlex></span>
            <button mat-raised-button color="primary" matStepperPrevious >Back</button>
           
          </div>
        </form>
    </mat-step>

  </mat-horizontal-stepper>
</mat-card>

  <!--
<div fxLayout="row" fxFlex fxLayoutGap="50px" fxLayoutAlign="center center">
  </div>
              -->
<pre>{{clientdetails.value | json}}</pre>
<pre>{{clientaddress.value | json}}</pre>
<pre>{{clientbank.value | json}}</pre>
<pre>{{clientfatca.value | json}}</pre>




assignvalue(){
    console.log("inside assignvalue");
    console.log(this.regdet.clientname);
	 this.clientdetails.controls.setValue(this.regdet);
